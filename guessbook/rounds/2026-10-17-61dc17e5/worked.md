# Worked answers, round 2026-10-17-61dc17e5

How each worked answer in `worked.json` was reached, written before anything was run.

**1. Longest increasing subsequence, n = 3,997.** 2√n − 1.7711·n^(1/6) = 126.444 − 7.056 = 119.388. The finite-size correction measured in earlier rounds was +0.45 at n = 872 and +0.53 at n = 261, perhaps shrinking slowly with n. Taking about +0.43 gives **119.82**. The simulation error is 0.11 and the correction is uncertain by about 0.12.

**2. Names in `warnings.__all__`.** Through 3.12 there are eight: warn, warn_explicit, showwarning, formatwarning, filterwarnings, simplefilter, resetwarnings, catch_warnings. 3.13 added the `deprecated` decorator from PEP 702, so **9**.

**3. Code points in category Me.** Listed from memory: U+0488–0489 (Cyrillic hundred-thousands and millions signs), U+1ABE (combining parentheses overlay), U+20DD–20E0 (enclosing circle, square, diamond, circle backslash), U+20E2–20E4 (enclosing screen, keycap, upward triangle), U+A670–A672 (Cyrillic ten-millions and up). That's 2 + 1 + 4 + 3 + 3 = **13**.

**4. Function definitions in `bdb`.** Counted from memory. The Bdb class has about 49 methods, including the 3.12 additions for opcode tracing. Then the module-level set_trace, Breakpoint's 8 methods, checkfuncname and effective, the test class Tdb's 4 methods, and foo, bar and test. Total about **67**.

**5. Draws until a repeat, d = 20,895.** √(πd/2) = √(32,821.789) = 181.16785. Adding 2/3, then (1/12)·√(π/(2d)) = 0.00072, then −4/(135d) gives **181.83524**. This formula has been right to 0.0001 in both earlier rounds.

**6. Primes in [1,134,200, 1,145,075].** That's 10,876 numbers at density 1 / 13.9462, so **780**. The standard deviation is about 12; earlier rounds' prime counts landed +1.0 and −0.5 standard deviations off.

**7. Lines in `socket`.** Recall: the Windows errorTab dictionary, the socket class with its sendfile machinery, fromfd, send_fds and recv_fds, the socketpair fallback, SocketIO, getfqdn, create_connection, has_dualstack_ipv6, create_server and getaddrinfo. About **975**.

**8. Unicode names with the word MATHEMATICAL.** The Mathematical Alphanumeric Symbols block has 996 assigned, all named MATHEMATICAL …. The Arabic Mathematical Alphabetic Symbols block has 143, all ARABIC MATHEMATICAL …. Ten MATHEMATICAL LEFT/RIGHT … BRACKET characters at U+27E6–27EF, and MATHEMATICAL RISING and FALLING DIAGONAL. Total **1,151**.

**9. Highest point of a 579-step walk.** N is odd, so E[M] = E|S₅₈₀| − ½ ≈ √(1,160/π)·(1 − 1/2,320) − ½ = 19.2073 − 0.5 = **18.707**. Simulation error 0.23.

**10. Collatz steps from 13,994,883,000.** The model's median for a random number this size is about 230, with quartiles near 180 and 290. But this is one specific number, not a random one. It ends in 000, so its first three steps are certainly halvings, which the model knows nothing about. Then I stopped estimating and traced the whole trajectory by hand, checking each 3n + 1 twice:

> 13,994,883,000 → (3 halvings) 1,749,360,375 → … → step 59: 88,761,481 → … → step 98: 351,455 → … → step 148: 31,703 → step 157: 13,375 → step 177: 3,571 → step 196: 53 → 160 → 80 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1

That's **207** steps. A single slip anywhere would make the answer meaningless, so I give it about 85%. The 90% interval keeps some room around the model's center for that case.

**11. Mean distance in a 1 × 1.5 rectangle.** Same exact formula as before: 0.444444 + 3.375 + 0.550848 + 2.5 × (1.406577 + 0.796509) = 9.878007, divided by 15 gives **0.65853**. Simulation error is about 0.0005.

**12. Assigned in the Runic block.** U+16A0–16EA letters (75), three punctuation marks, three golden numbers, and eight letters added in Unicode 7 (U+16F1–16F8). That makes **89**, with U+16F9–16FF unassigned.
