# Clean Code Rules for AI Code Generation

Write code a human can read top to bottom without jumping around.
When these rules conflict with ponytail.md or Karpathy.md (simplicity, no unrequested abstractions), those win.

## Meaningful Names
- Use intention-revealing names that explain why something exists
- Avoid vague names (`data`, `info`, `manager`, `helper`, `util`, `handle`) unless nothing more specific fits
- Use pronounceable, searchable names; short names (`i`, `x`) only in tiny scopes
- Class names: nouns (e.g., `UserAccount`). Function names: verbs (e.g., `calculateTotal`)
- No Hungarian notation or type prefixes
- Follow the language's naming convention (snake_case in Python/C, camelCase in JS/TS)

## Abstraction: Less Is More
- Do not split code into functions just to make functions short. Extract a function only when it is
  reused, or when the extracted piece has a clear name and hides real complexity
- A 30-40 line function that reads straight down is better than five 6-line functions the reader must chase
- No single-use helpers, wrapper classes, interfaces, factories, builders, or dependency injection
  unless explicitly requested or already used by the project
- Prefer plain functions and plain data (dicts, structs, objects) over classes when there is no state to protect
- Prefer a simple `if`/`switch` over polymorphism or strategy patterns for a handful of cases
- No layers of indirection "for the future" (YAGNI)

## Module Layout: One Main File Per Module (projects only)
Before applying this section, check both:
1. The code goes inside an existing project that is already split into module folders
   (e.g., `src/m6-friends/`, `src/m7-chat/`), or the user explicitly asks for a new module
2. The code belongs to one of those modules (not a standalone script in `scripts/`, a test, or a config)

Both yes → follow the rules below. Otherwise (one-off script, snippet, exercise, quick tool, or unsure)
→ skip this section entirely and write ONE file. Never create folders, `types.ts`, or helper files
just to satisfy these rules.

- Each module folder has exactly one main file. All main functions (including API routes) live there.
  Name: follow the project's existing convention (e.g., `routes.ts`); if there is none, use `index.ts`
  in TypeScript, and in Python a file named after the module, with `__init__.py` only re-exporting it
- Every other file in the folder is a helper file, called only from within the same module
- Calls go one way: main → helper → lower-level helper. Never call back up, no mutual calls between
  helpers at the same level (move shared code one level down), max 2-3 levels deep
- Helpers never import the main file. Shared types go in `types.ts` (Python: `models.py`)
- Other modules import only from a module's main file, never from its helper files
- When the main file is too long to read in one sitting, the module does too much: split it into two modules

## Functions
- Order functions top-down in every file: a caller comes before the functions it calls
- Do one thing; one level of abstraction per function
- Limit arguments: 0-3; group more into one object/struct; avoid boolean flag arguments
- No hidden side effects - a function does what its name says
- Return early for error / edge cases instead of deep nesting (max ~3 levels of indentation)

## Density: Don't Cram
- One statement per line. No multiple statements joined with `;` or `,`
- No nested ternaries. One simple ternary is fine; otherwise use `if`/`else`
- Break long call chains (more than ~3 calls) into named intermediate variables or one call per line
- No clever one-liners that need a second read (dense comprehensions, chained `&&`/`||` tricks, bit hacks
  without a comment). Readability beats line count
- Name complex conditions: `const isExpired = now > deadline && !renewed` then `if (isExpired)`
- Type, interface, struct, and class definitions: one field per line, even if they would fit on one line.
  Put a line break right after the opening `{` so formatters (Biome, Prettier) keep it expanded:
  ```ts
  // Bad
  type CodeCheck = { lockedUntil: Date | null; owner: CodeOwner | undefined };

  // Good
  type CodeCheck = {
    lockedUntil: Date | null;
    owner: CodeOwner | undefined;
  };
  ```
- Line length: aim for 100 characters, hard limit 120

## Blank Lines: Split Code Into Paragraphs
Blank lines show which comment belongs to which block. Formatters keep blank lines and collapse
repeated ones, but never add them, so add them yourself:
- Put a blank line before a comment that describes a block of code (except right after an opening `{` / `:`)
- Inside a function, separate each step with a blank line, e.g. validate input → compute → log → return
- Put a blank line after an `if` block that ends with `return` / `throw` / `break` / `continue`,
  before the next step
- Put a blank line between top-level functions, classes, and groups of constants
  (use two in Python, per PEP 8)
- Keep lines that do one thing together with no blank line between them, e.g. several related
  constants, or a log line and the `return` right after it
- Never use extra spaces to align `=`, values, or trailing comments across lines

Example:
```ts
function applyDiscount(order: Order, code: string): number {
  if (!order.items.length) {
    throw new Error(`Order ${order.id} has no items`);
  }

  const subtotal = sumPrices(order.items);
  const discount = lookupDiscount(code);

  // Discounts never push the total below zero
  const total = Math.max(subtotal - discount, 0);

  logger.info(`Order ${order.id}: ${subtotal} -> ${total}`);
  return total;
}
```

## Comments
- Code should explain *what*; comments explain *why* (intent, constraints, non-obvious decisions)
- Good: warnings, TODOs, public API docs, the reason behind a weird-looking line
- Bad: restating the code, banner/divider comments, changelog comments, commented-out code
- A short comment above a block of steps is fine when it saves the reader from decoding the block

## Error Handling
- Handle errors where you can actually do something about them; let the rest propagate
- No try/catch around code that cannot fail, and no catch blocks that silently swallow errors
- No fallback defaults that hide bugs (e.g., `?? 0`, `or []`) unless the default is truly correct
- Error messages include context: what failed and with which input
- Validate at trust boundaries (user input, files, network), not on every internal call

## Classes and Data
- Small classes, one responsibility; only create a class when there is state plus behavior on it
- Law of Demeter: avoid long `a.getB().getC().doSomething()` reach-throughs
- No blind getters/setters for every field; plain data can just be plain data
- Favor composition over inheritance; avoid inheritance deeper than one level

## Tests
- Fast, independent, repeatable, self-validating
- One concept per test (several asserts on the same result are fine)
- Test names describe the behavior: `rejects_expired_token`, not `test1`
- Arrange - Act - Assert, separated by blank lines
- No mocks/fixtures/frameworks beyond what the project already uses

## Code Smells to Avoid
- Duplicate code (but tolerate a little duplication over a premature abstraction)
- Dead code: unused variables, functions, parameters, imports
- Long parameter lists
- Magic numbers and strings - give them a named constant
- Deep nesting
- Functions that need scrolling *and* jumping to understand

## Language Notes

### Python
- Follow PEP 8; use type hints on function signatures
- Use f-strings, `pathlib`, `with` for files/resources, `dataclass` for plain records
- A list comprehension is fine if it fits on one line and has at most one `if`; otherwise use a loop
- Catch specific exceptions, never bare `except:`

### TypeScript / JavaScript
- `const` by default, `let` only when reassigned, never `var`
- Use `async`/`await` over `.then()` chains
- Prefer `type`/plain objects over classes for data; avoid `any` (use `unknown` and narrow)
- Use optional chaining `?.` for genuinely optional data, not to silence errors
- Always use braces for `if`/`else`, even single-line bodies

### Bun
Applies when the user says to use Bun, or the project has `bun.lock` / `bunfig.toml`.
- Prefer Bun-native APIs over Node equivalents: `Bun.env` over `process.env`, `Bun.file` / `Bun.write`
  over `node:fs`, `Bun.SQL` over a database client package, `bun:test` over Jest/Vitest
- Use Node APIs only when Bun has no equivalent (e.g., `process.exit`)

### C / C++
- Always use braces, even for one-line `if`/`for` bodies
- One declaration per line; initialize variables when declared
- Check return values of calls that can fail (`malloc`, `fopen`, syscalls) and clean up on every path
- C++: prefer RAII, `std::vector`/`std::string`, and references over raw pointers and manual `new`/`delete`
- Name constants with `const`/`constexpr`/`enum` rather than `#define` when possible

---

**Core Philosophy**: Code is read far more than it is written. Optimize for a reader going top to bottom:
simple, spaced out, and no more abstraction than the problem needs.
