# System Resource Guide

Curated starting points for studying well-known systems. Organized by category. For each system, resources are listed in recommended study order.

---

## Messaging & IPC

### Aeron

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Martin Thompson: "Why Aeron?" (blog) | Origin story |
| Architecture | Aeron Design Overview (GitHub wiki) | Design doc |
| Deep dive | "Aeron: Open-source High-Performance Messaging" (Strange Loop talk) | Conference talk |
| Design decisions | Martin Thompson: "Adventures with Concurrent Programming" (QCon) | Creator talk |
| Comparison | Aeron vs ZeroMQ benchmarks and design discussion | Community analysis |

**Key concepts:** Media driver, log buffers, memory-mapped IPC, UDP + custom reliability, credit-based flow control

### LMAX Disruptor

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Martin Fowler: "The LMAX Architecture" (blog) | Origin story |
| Architecture | LMAX Disruptor technical paper | Design paper |
| Deep dive | "Mechanical Sympathy" (QCon talk by Martin Thompson) | Creator talk |
| Principles | Martin Thompson's Mechanical Sympathy blog | Ongoing resource |

**Key concepts:** Ring buffer, single-writer principle, false sharing prevention, sequence barriers, cache-line padding

### Apache Kafka

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Kafka: a Distributed Messaging System for Log Processing" (LinkedIn, 2011) | Original paper |
| Architecture | Jay Kreps: "The Log: What every software engineer should know" (blog) | Foundational article |
| Deep dive | "Kafka Internals" (Confluent talks, multiple parts) | Talk series |
| Design decisions | Jay Kreps: "I Heart Logs" (O'Reilly book, short) | Book |

**Key concepts:** Append-only log, consumer groups, partition-based parallelism, sendfile() zero-copy, page cache delegation, ISR replication

### SBE (Simple Binary Encoding)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Simple Binary Encoding" (Real Logic blog) | Origin |
| Architecture | SBE specification (GitHub) | Design spec |
| Comparison | SBE vs Protobuf vs FlatBuffers vs Avro benchmarks | Community benchmarks |

**Key concepts:** Zero-copy decoding, flyweight pattern over buffer, no allocation on decode, schema-driven code generation

---

## Storage Engines & Databases

### RocksDB

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Facebook: "Under the Hood: Building and open-sourcing RocksDB" (blog) | Origin story |
| Architecture | RocksDB Wiki — Architecture Guide | Design doc |
| Deep dive | "RocksDB Internals" (Data@Scale talk) | Conference talk |
| Tuning = architecture | RocksDB Tuning Guide (wiki) | Design-through-configuration |

**Key concepts:** LSM tree, write-ahead log, memtable, SST files, compaction strategies (leveled, universal, FIFO), bloom filters, block cache

### TigerBeetle

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | TigerBeetle Design Document (tigerbeetle.com) | Design doc |
| Architecture | "Deterministic Simulation Testing" (blog) | Key innovation |
| Deep dive | Joran Dirk Greef talks (various conferences) | Creator talks |

**Key concepts:** Deterministic simulation testing, io_uring, direct I/O (bypass page cache), fixed-schema for financial transactions, consensus (Viewstamped Replication)

### SQLite

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Appropriate Uses For SQLite" (sqlite.org) | Design philosophy |
| Architecture | "Architecture of SQLite" (sqlite.org) | Official design doc |
| Deep dive | "SQLite Internals: How The World's Most Used Database Works" (book by Sibsankar Haldar) | Deep architecture |

**Key concepts:** Single-file database, B-tree storage, WAL mode, serverless design, testing methodology (100% branch coverage)

---

## Networking & I/O

### io_uring

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "The rapid growth of io_uring" (LWN.net) | Origin story |
| Architecture | "Lord of the io_uring" (unixism.net tutorial) | Tutorial-as-architecture |
| Deep dive | Jens Axboe's kernel talks | Creator talks |
| Comparison | io_uring vs epoll vs aio benchmarks | Community analysis |

**Key concepts:** Submission/completion ring buffers, shared memory between kernel and userspace, registered buffers, linked operations, kernel-side polling

### DPDK (Data Plane Development Kit)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Intel: "DPDK: Data Plane Development Kit" (overview) | Origin |
| Architecture | DPDK Programmer's Guide — Architecture Overview chapter | Design doc |
| Deep dive | "Kernel Bypass Networking" talks (various DPDK summits) | Conference talks |

**Key concepts:** Poll-mode drivers, hugepages, NUMA-aware memory allocation, lockless ring buffers, zero-copy packet processing, kernel bypass

### Netty

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Netty in Action" chapters 1-3 (Manning) | Origin + architecture |
| Architecture | Netty architecture overview (netty.io) | Design doc |
| Deep dive | Norman Maurer talks on Netty internals | Creator talks |

**Key concepts:** Event loop, channel pipeline, ByteBuf (reference-counted buffers), zero-copy composite buffers, native transport (epoll/io_uring)

---

## Concurrency & Coordination

### Raft Consensus

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "In Search of an Understandable Consensus Algorithm" (Ongaro & Ousterhout, 2014) | Original paper |
| Architecture | The Raft visualization (thesecretlivesofdata.com/raft) | Interactive |
| Deep dive | Diego Ongaro's PhD thesis: "Consensus: Bridging Theory and Practice" | Complete reference |
| Optimization | "Pipelining Raft" and "Multi-Raft" discussions | Performance extensions |

**Key concepts:** Leader election, log replication, safety guarantees, joint consensus for membership changes, snapshot & compaction

### ZooKeeper / Zab

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "ZooKeeper: Wait-free coordination for Internet-scale systems" (USENIX ATC 2010) | Original paper |
| Architecture | ZooKeeper Internals (cwiki.apache.org) | Design doc |
| Comparison | ZooKeeper vs etcd vs Consul design comparison | Community analysis |

**Key concepts:** Zab protocol, znodes, watches, ephemeral nodes, sequential consistency model, session management

---

## Caching

### Caffeine (W-TinyLFU)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Ben Manes: "Design of a Modern Cache" (blog/talk) | Origin story |
| Architecture | "TinyLFU: A Highly Efficient Cache Admission Policy" (paper) | Academic paper |
| Deep dive | Caffeine wiki — design and benchmarks | Design doc |

**Key concepts:** W-TinyLFU admission policy, count-min sketch for frequency estimation, window + main space (LRU + SLRU), near-optimal hit rate

### Redis

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Salvatore Sanfilippo: "Redis Manifesto" | Design philosophy |
| Architecture | Redis Internals documentation (redis.io) | Design doc |
| Deep dive | "Redis in Action" architecture chapters | Deep reference |

**Key concepts:** Single-threaded event loop, data structures as first-class operations, RDB + AOF persistence, replication, Cluster hash slots

---

## Congestion Control & Flow Control

### BBR (Bottleneck Bandwidth and Round-trip propagation time)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "BBR: Congestion-Based Congestion Control" (Google, ACM Queue 2016) | Original paper |
| Architecture | Neal Cardwell talks at IETF | Creator talks |
| Comparison | BBR vs CUBIC vs Reno — design philosophy differences | Community analysis |

**Key concepts:** Model-based (not loss-based), bandwidth-delay product estimation, probe bandwidth / probe RTT cycles, fairness behavior

---

## Cross-System Principle Index

Quick lookup: which systems demonstrate which principle.

| Principle | Systems |
|-----------|---------|
| Zero-allocation hot path | Disruptor, Aeron, SBE, Chronicle Queue |
| Kernel bypass | DPDK, io_uring, Aeron (mmap IPC) |
| Sequential I/O over random | Kafka, RocksDB (LSM), any WAL-based system |
| Single-writer principle | Disruptor, LMAX architecture |
| Mechanical sympathy | Disruptor, Aeron, DPDK |
| Append-only log | Kafka, RocksDB (WAL), TigerBeetle |
| Back-pressure over buffering | Aeron, Reactive Streams, Disruptor |
| Let the OS do what it's good at | Kafka (page cache), RocksDB (mmap reads) |
| Batching / amortization | Kafka (batch produce/fetch), Raft (log batching), io_uring (batch submission) |
| Deterministic testing | TigerBeetle, FoundationDB |
| Cache-friendly layout | Disruptor (ring buffer), DPDK (hugepages), any SoA design |
