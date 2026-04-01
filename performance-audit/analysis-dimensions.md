# Analysis Dimensions — Deep Dive

Detailed patterns, code examples, and detection strategies for each of the 10 performance audit dimensions.

## D1: Memory Allocation & GC Pressure — Extended

### Detection Strategy

1. Search for `new` keyword on hot paths (Java/C#/C++)
2. Look for autoboxing: `Map<String, Integer>` with `int` values being boxed
3. Find string concatenation with `+` in loops (creates intermediate `StringBuilder` + `String` per iteration)
4. Identify lambda captures that close over mutable state (creates new closure object per invocation)
5. Check for `toArray()`, `toList()`, `stream().collect()` on hot paths

### Example: QuickFIX Message Parsing (Illustrative)

**Problematic pattern:**
```java
// Per-message: new Message, new HashMap for fields, new String per field
Message msg = new Message(rawFixString);
String orderId = msg.getString(ClOrdID.FIELD);  // allocation
String symbol = msg.getString(Symbol.FIELD);     // allocation
```

**Chronicle FIX approach:**
```java
// Flyweight reader over reusable buffer — zero allocation
fixReader.reset(buffer, offset, length);
fixReader.readField(ClOrdID.FIELD, orderIdBuilder);  // writes into pre-allocated StringBuilder
fixReader.readField(Symbol.FIELD, symbolBuilder);     // reuses builder
```

### What to Count

- Allocations per operation (not per startup)
- Total bytes allocated per operation
- Object survival rate (do they escape to old gen?)
- TLAB (Thread-Local Allocation Buffer) overflow frequency

---

## D2: Data Copying & Serialization — Extended

### Detection Strategy

1. Look for `getBytes()` / `new String(bytes)` round-trips
2. Find `ByteBuffer.wrap()` followed by get operations that copy
3. Identify `toByteArray()` on streams
4. Search for `clone()`, `Arrays.copyOf()`, `System.arraycopy()` on hot paths
5. Check for `ObjectOutputStream` / `ObjectInputStream` (Java serialization — extremely slow)

### The Serialization Tax

Every representation change costs CPU and memory:

```
Wire bytes → ByteBuffer → String → Domain Object → String → ByteBuffer → Wire bytes
     Copy 1       Copy 2      Parse      Serialize    Copy 3      Copy 4
```

**Optimized:**
```
Wire bytes → Flyweight view (no copy) → Write directly to output buffer
                  Zero-copy read              Single copy
```

### Common Offenders

| Pattern | Cost | Fix |
|---------|------|-----|
| `new String(bytes, "UTF-8")` then `string.getBytes("UTF-8")` | 2 full copies + charset codec | Keep as bytes, parse in-place |
| Java Serialization (`Serializable`) | 10-50x slower than binary protocols | Use Protobuf, FlatBuffers, SBE, Chronicle Wire |
| JSON parse → modify → JSON serialize | Full parse + full serialize | Use streaming JSON (Jackson streaming) or binary format |
| `ByteArrayOutputStream.toByteArray()` | Copies entire buffer | Use direct buffer access or pre-sized buffer |

---

## D3: I/O & Network Patterns — Extended

### Detection Strategy

1. Find socket reads/writes not wrapped in buffered streams
2. Look for synchronous HTTP calls in request handlers
3. Identify `Connection.createStatement()` per query (no prepared statements)
4. Check for file I/O on request-handling threads
5. Search for `Thread.sleep()` as synchronization mechanism
6. Find DNS lookups (hostname resolution) on hot paths

### Blocking I/O Multiplier

In a thread-per-request model with blocking I/O:
- 1ms network wait = 1ms of thread blocked
- 1000 concurrent requests = 1000 threads blocked
- OS scheduling overhead grows quadratically with thread count

### Socket-Level Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| No TCP_NODELAY | 40ms Nagle delay on small messages | Set `TCP_NODELAY = true` |
| Small recv buffer | Multiple syscalls per message | Increase `SO_RCVBUF` |
| Blocking accept loop | Single-threaded accept bottleneck | Use `epoll`/`kqueue`/`io_uring` |
| Per-message flush | Syscall per message | Batch flush / writev |

---

## D4: Lock Contention & Synchronization — Extended

### Detection Strategy

1. Search for `synchronized` blocks/methods on hot paths (Java)
2. Find `Lock.lock()` / `Lock.unlock()` patterns
3. Look for `Collections.synchronizedMap()` in multi-threaded code
4. Identify `AtomicReference.compareAndSet()` in retry loops
5. Check for `volatile` fields read in tight loops
6. Find `ConcurrentHashMap` operations that take segment locks unnecessarily

### Contention Patterns

**Lock convoy:** Multiple threads queue behind one lock, creating serialized execution even on multi-core.

**Priority inversion:** Low-priority thread holds lock needed by high-priority thread.

**False sharing:** Two unrelated fields on the same cache line; concurrent writes to either cause cache invalidation across cores.

```java
// False sharing: counter1 and counter2 likely on same 64-byte cache line
class Counters {
    volatile long counter1;  // Core 0 writes this
    volatile long counter2;  // Core 1 writes this — invalidates Core 0's cache
}

// Fix: padding or @Contended annotation (Java)
class Counters {
    @jdk.internal.misc.Contended
    volatile long counter1;
    @jdk.internal.misc.Contended
    volatile long counter2;
}
```

---

## D5: Data Structure & Algorithm Choice — Extended

### Detection Strategy

1. Check collection types against access patterns (random access? iteration? lookup?)
2. Find `List.contains()` or `List.indexOf()` on large lists (should be `Set` or `Map`)
3. Look for `TreeMap` where `HashMap` suffices (no range queries needed)
4. Identify `LinkedList` usage (almost always worse than `ArrayList`)
5. Find growing `ArrayList` without initial capacity hint
6. Check for hash map load factors and initial sizing

### Cache Locality Impact

| Structure | Cache Behavior | Use When |
|-----------|---------------|----------|
| `int[]` / primitive array | Excellent — contiguous, prefetchable | Sequential or random access on primitives |
| `ArrayList<T>` | Good — contiguous array of references | Random access, iteration |
| `HashMap<K,V>` | Moderate — array of buckets + chained entries | Key-value lookup |
| `LinkedList<T>` | Poor — pointer chasing, scattered memory | Almost never (use `ArrayDeque` instead) |
| `TreeMap<K,V>` | Poor — tree nodes scattered in memory | Only when you need sorted range queries |

---

## D6: Thread & Concurrency Model — Extended

### Detection Strategy

1. Find thread pool configurations (core size, max size, queue type)
2. Look for `Executors.newCachedThreadPool()` (unbounded, dangerous)
3. Identify `Executors.newFixedThreadPool()` with blocking I/O (thread exhaustion)
4. Check for `CompletableFuture` chains that block (`join()` / `get()`) on I/O threads
5. Find `Thread.sleep()` for timing (use `ScheduledExecutorService`)
6. Look for missing backpressure in producer-consumer patterns

### Thread Model Trade-offs

| Model | Latency | Throughput | Complexity | Best For |
|-------|---------|------------|------------|----------|
| Thread-per-request | Low (if few) | Limited by threads | Low | Simple CRUD APIs (<1K concurrent) |
| Event loop (Netty, Node) | Very low | Very high | Medium | I/O-bound workloads, proxies |
| Thread pool + queues | Medium | High | Medium | CPU-bound processing |
| Virtual threads (Java 21+) | Low | Very high | Low | Blocking I/O at scale |
| Single-threaded (Disruptor) | Ultra-low | Very high | High | Latency-critical message processing |

---

## D7: Caching & Memoization — Extended

### Detection Strategy

1. Search for repeated identical database queries in a request lifecycle
2. Find `Pattern.compile()` inside methods (should be `static final`)
3. Look for `Class.forName()`, `getMethod()`, `getDeclaredField()` in loops
4. Identify configuration reads from file/DB per request
5. Check for DNS resolution caching (`InetAddress` caching in Java)
6. Find expensive computations (crypto, compression) with repeating inputs

### Cache Sizing Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| No size limit | Memory leak (OOM) | Set max entries, use LRU eviction |
| No TTL | Stale data | Time-based expiry |
| Per-thread cache without bound | N threads × cache size memory | Shared cache with concurrent access |
| Caching mutable objects | Corruption from shared mutation | Cache immutable copies or deep-copy on read |

---

## D8: Logging & Observability Overhead — Extended

### Detection Strategy

1. Find `log.debug("message: " + expensiveObject.toString())` — string built even when debug disabled
2. Look for logging inside inner loops
3. Check if log appenders are synchronous (blocking I/O on log write)
4. Find metric collection with unbounded cardinality (metric per user ID)
5. Identify full stack trace generation for non-exceptional events

### Cost Comparison

| Pattern | Cost per Call |
|---------|-------------|
| `log.isDebugEnabled()` guard | ~1ns |
| `log.debug("msg: {}", obj)` (SLF4J parameterized) | ~10ns when disabled |
| `log.debug("msg: " + obj.toString())` | ~1µs+ (string concat + toString always runs) |
| `log.debug(...)` with sync file appender | ~100µs+ (disk I/O) |

---

## D9: Memory Layout & CPU Cache — Extended

### Detection Strategy

1. Identify hot fields scattered across large objects
2. Find `Map<Long, Long>` (should be primitive long-long map like Eclipse Collections or Koloboke)
3. Look for `List<Integer>` (boxed integers waste 16 bytes per entry vs 4 bytes unboxed)
4. Check array-of-structs vs struct-of-arrays for columnar access
5. Find random access over large datasets (defeats prefetcher)

### Memory Overhead (Java)

| Type | Memory per Element | Overhead vs Primitive |
|------|-------------------|----------------------|
| `int` | 4 bytes | baseline |
| `Integer` | 16 bytes (object header + value + padding) | 4x |
| `int[]` (1000 elements) | ~4 KB | baseline |
| `ArrayList<Integer>` (1000 elements) | ~20 KB (array + 1000 Integer objects) | 5x |
| `HashMap<Integer, Integer>` (1000 entries) | ~48 KB (entries + keys + values + buckets) | 12x |

---

## D10: Error Handling & Exception Cost — Extended

### Detection Strategy

1. Find `catch` blocks that catch broad exceptions (`Exception`, `Throwable`) in hot paths
2. Look for exceptions used for flow control (`try { parse(...) } catch (NumberFormatException) { ... }`)
3. Identify `Exception` constructors with stack trace on hot paths
4. Check for exception wrapping chains (wrap → catch → wrap → catch)
5. Find `Optional.of()` / `Optional.empty()` allocation per call on hot paths

### Exception Cost (JVM)

| Operation | Approximate Cost |
|-----------|-----------------|
| `throw new Exception()` (with stack trace) | ~5-50 µs (depends on stack depth) |
| `throw CACHED_EXCEPTION` (pre-created, no fill) | ~0.1 µs |
| Return error code / sentinel value | ~1 ns |
| `Optional.empty()` (cached singleton) | ~1 ns |
| `Optional.of(value)` (new allocation) | ~5-10 ns |

Stack trace filling (`fillInStackTrace`) is the expensive part. For expected errors on hot paths, either pre-create exceptions with overridden `fillInStackTrace` or use return-code patterns.
