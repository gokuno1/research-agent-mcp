# Language-Specific Performance Anti-Patterns

Quick-reference for the most impactful anti-patterns per language/runtime. Organized by language, then by severity.

---

## Java / JVM

### Critical (P0 on hot paths)

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| Java Serialization (`Serializable`) | Reflection-heavy, generates metadata per call, ~50x slower than binary | Use SBE, Protobuf, FlatBuffers, or Chronicle Wire |
| `synchronized` on hot method | Serializes all callers, contention grows with cores | Lock striping, `ReadWriteLock`, `StampedLock`, or lock-free |
| `String` concatenation in loops | New `StringBuilder` + `String` each iteration | Single `StringBuilder` outside loop |
| `HashMap<String, Object>` with per-message allocation | GC pressure: N entries × (Entry + Key + Value) per message | Flyweight, object pool, or off-heap (Chronicle Map) |
| Blocking I/O in NIO event loop (Netty handler) | Blocks event loop thread, kills throughput | Offload to separate executor or use async I/O |

### High (P1 on hot paths)

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| Autoboxing (`int` → `Integer`) | 16 bytes per boxed int, GC churn | Use primitive collections (Eclipse Collections, HPPC) |
| `Collections.synchronizedMap()` | Global lock on every operation | `ConcurrentHashMap` or lock-free alternatives |
| Reflection (`getMethod`, `getField`) | 10-100x slower than direct call | Cache `MethodHandle`, use code generation |
| `Pattern.compile()` per invocation | Regex compilation is expensive | `static final Pattern` |
| `SimpleDateFormat` per call (not thread-safe, so often re-created) | Allocation + parsing setup | `DateTimeFormatter` (immutable, thread-safe) |
| Exception for flow control | Stack trace ~5-50µs | Return codes, `Optional`, pre-validated input |

### Medium (P2-P3)

| Anti-Pattern | Fix |
|-------------|-----|
| `LinkedList` usage | Replace with `ArrayList` or `ArrayDeque` |
| `TreeMap` when no range queries | Replace with `HashMap` |
| Unbounded `Executors.newCachedThreadPool()` | Use bounded pool with rejection policy |
| `System.currentTimeMillis()` in tight loops | Cache timestamp, use `System.nanoTime()` for intervals |
| Excessive `Optional` wrapping on hot path | Return nullable + null-check on hot paths |

### JVM Tuning Signals

Look for these in startup scripts, Dockerfiles, or JVM flags:
- Missing `-XX:+UseG1GC` or `-XX:+UseZGC` (defaulting to Serial/Parallel on small heaps)
- No `-Xms` = `-Xmx` (heap resizing pauses)
- No `-XX:+AlwaysPreTouch` (page faults on first access)
- Missing `-XX:-TieredCompilation` or C2 warmup awareness for latency-sensitive apps
- No GC logging enabled (`-Xlog:gc*` on Java 11+)

---

## Python

### Critical

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| GIL-bound CPU work in threads | Only one thread runs Python at a time | `multiprocessing`, C extensions, or `concurrent.futures.ProcessPoolExecutor` |
| Nested loops over large data | Pure Python loop overhead ~100ns per iteration | NumPy vectorization, list comprehensions, or Cython |
| Repeated attribute lookup in loops (`obj.method()`) | Attribute resolution per call | Local variable binding: `m = obj.method` before loop |
| `+` string concatenation in loops | New string object per concat | `''.join(parts)` or `io.StringIO` |

### High

| Anti-Pattern | Fix |
|-------------|-----|
| `import` inside functions on hot paths | Move to module level |
| `global` variable access in tight loops | Bind to local variable |
| `dict` as struct (string key lookup per field) | `dataclass`, `namedtuple`, or `__slots__` |
| Creating regex per call (`re.match(pattern, s)`) | `re.compile(pattern)` and reuse |
| `list.append()` in loop building large list | Pre-allocate if size known, or use generator |

---

## Go

### Critical

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| Excessive goroutine creation per request | Allocation + scheduling overhead | Goroutine pools or bounded concurrency |
| `interface{}` / `any` in hot paths | Prevents compiler optimization, requires type assertion | Concrete types or generics (Go 1.18+) |
| Unbuffered channels in producer-consumer | Synchronization point per send/recv | Buffered channels |
| `fmt.Sprintf` in hot paths | Reflection, allocation | `strconv.AppendInt`, `[]byte` builders |

### High

| Anti-Pattern | Fix |
|-------------|-----|
| `sync.Mutex` protecting read-heavy data | `sync.RWMutex` |
| Slice growing without capacity hint | `make([]T, 0, expectedCap)` |
| `map` access in hot loops (random memory access) | Sorted slice for small datasets, `sync.Map` for concurrent |
| `defer` in tight inner loops | Move defer outside loop or use explicit cleanup |
| JSON `encoding/json` (reflection-based) | `easyjson`, `sonic`, or `encoding/json/v2` |

---

## C / C++

### Critical

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| `malloc`/`free` per message | Allocator overhead + fragmentation | Arena allocator, object pool, stack allocation |
| Virtual function calls in tight loops | Indirect branch, defeats inlining | CRTP (C++), function pointers with likely targets, devirtualization hints |
| `std::map` (tree-based) for lookup-heavy workload | Pointer chasing, poor cache locality | `std::unordered_map`, or flat hash map (abseil, robin-hood) |
| `std::shared_ptr` in hot paths | Atomic reference counting per copy | Raw pointer with clear ownership, `unique_ptr` |
| Cache-unfriendly AoS (array of structs) for columnar access | Loads unused fields into cache line | SoA (struct of arrays) |

### High

| Anti-Pattern | Fix |
|-------------|-----|
| `std::string` copies (copy-on-write removed in C++11) | `std::string_view`, move semantics |
| `std::vector<bool>` (bit-packed, not a real vector) | `std::vector<char>` or `std::bitset` |
| Exceptions in hot paths | Error codes, `std::expected` (C++23) |
| `std::endl` (flushes stream) | `'\n'` for newline without flush |
| Missing `constexpr` / `consteval` | Compute at compile time where possible |

---

## Rust

### Critical

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| Excessive `.clone()` on hot paths | Heap allocation per clone | Borrow (`&T`), `Cow<T>`, or `Arc<T>` |
| `Box<dyn Trait>` in tight loops | Vtable dispatch, heap allocation | Generics with monomorphization, enum dispatch |
| `String` / `Vec` allocation per iteration | Allocator pressure | Reuse buffers, `with_capacity()` |
| Unnecessary `async` overhead for CPU-bound work | Future state machine overhead, executor scheduling | Synchronous code or `spawn_blocking` |

### High

| Anti-Pattern | Fix |
|-------------|-----|
| `HashMap` with default hasher (SipHash — safe but slow) | `ahash`, `FxHashMap` for non-adversarial input |
| `Mutex` contention across async tasks | `tokio::sync::RwLock`, sharding |
| `format!` in hot paths | Pre-allocated `String` with `write!` |
| Missing `#[inline]` on small hot functions across crate boundaries | Add `#[inline]` or `#[inline(always)]` |

---

## JavaScript / TypeScript (Node.js)

### Critical

| Anti-Pattern | Why It's Slow | Fix |
|-------------|---------------|-----|
| Blocking the event loop (CPU-heavy sync code) | Starves all other requests | `worker_threads`, chunked processing, or native addon |
| `JSON.parse` / `JSON.stringify` on large objects per request | Full parse/serialize, GC pressure | Streaming JSON, binary protocol, or caching |
| Unbounded `Promise.all` (thousands of concurrent I/O ops) | Memory spike, connection exhaustion | Batch with concurrency limit (`p-limit`) |

### High

| Anti-Pattern | Fix |
|-------------|-----|
| Object spread `{...obj}` in tight loops | Shallow copy cost; mutate in place or use immutable structure |
| `Array.push` growing massive arrays | Pre-allocate, use `TypedArray` for numeric data |
| `new Date()` per log entry in tight loop | Cache timestamp per batch |
| Dynamic `require()` / `import()` on hot paths | Static import at module level |
| Excessive `try/catch` in hot loops | Move try/catch outside loop body |

---

## Cross-Language Themes

These patterns hurt performance regardless of language:

1. **Allocation on hot paths** — every language has some form of this (heap, GC, ref-counting)
2. **Blocking I/O on processing threads** — universal throughput killer
3. **String manipulation in loops** — strings are immutable in most languages; concatenation = copy
4. **Wrong data structure for access pattern** — linked vs contiguous, tree vs hash
5. **Global locks on shared mutable state** — serializes multi-core execution
6. **Serialization round-trips** — wire → object → wire is always expensive
7. **Exception/error handling for control flow** — stack unwinding is not free
8. **Missing pre-computation / caching** — re-deriving what could be stored
