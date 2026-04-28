# Rust Coding Standards & Best Practices

## 1. Introduction
This document provides coding standards and best practices for developing applications in Rust. The goal is to leverage Rust's safety and performance features while ensuring the code is readable, maintainable, and idiomatic.

## 2. Guiding Principles
- **Safety First**: Embrace Rust's ownership and borrowing rules to prevent memory-related bugs at compile time. Avoid `unsafe` code unless absolutely necessary and well-documented.
- **Clarity and Readability**: Write code that is easy for other developers to understand. Prefer clear, explicit code over overly clever or concise code.
- **Performance**: Write performant code by default, but avoid premature optimization. Profile the application to identify and address bottlenecks.
- **Error Handling**: Use Rust's `Result` and `Option` enums for robust error handling. Avoid panicking in library code.

## 3. Code Organization
- **Crates and Modules**: Organize code into crates and modules that reflect the application's domain.
- **`main.rs` and `lib.rs`**: Use `main.rs` for application entry points and `lib.rs` for library code.
- **File Naming**: Use `snake_case` for file and directory names.

### Example Structure
```
my_project/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── lib.rs
    ├── api/
    │   ├── mod.rs
    │   └── routes.rs
    └── models/
        ├── mod.rs
        └── user.rs
```

## 4. Naming Conventions
- **Types (Structs, Enums, Traits)**: `PascalCase` (e.g., `struct User`, `enum Status`).
- **Functions, Methods, Variables, Modules**: `snake_case` (e.g., `fn get_user()`, `let user_name`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `const MAX_CONNECTIONS: u32 = 100;`).
- **Macros**: `snake_case!` (e.g., `println!`).

## 5. Error Handling
- **Use `Result<T, E>`**: For functions that can fail, return a `Result`. The error type `E` should implement the `std::error::Error` trait.
- **The `?` Operator**: Use the `?` operator to propagate errors cleanly.
- **Custom Error Types**: Define custom error enums for different failure modes in your application. Libraries like `thiserror` can simplify this.

### Example
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MyError {
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
    #[error("user not found")]
    NotFound,
}

async fn get_user(id: i32) -> Result<User, MyError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(pool)
        .await?
        .ok_or(MyError::NotFound)?;
    Ok(user)
}
```

## 6. Concurrency
- **Prefer `async/await`**: For I/O-bound tasks, use `async/await` with a runtime like `tokio` or `async-std`.
- **Use Channels for Communication**: For communication between threads or tasks, use channels (e.g., `tokio::sync::mpsc`).
- **Leverage `Arc<Mutex<T>>`**: For sharing state across threads, use `Arc<Mutex<T>>` or `Arc<RwLock<T>>` to ensure safe concurrent access.

## 7. Tooling
- **`rustfmt`**: Automatically format code according to the official Rust style guidelines. All code MUST be formatted with `rustfmt`.
- **`clippy`**: Use Clippy for linting. Address all Clippy warnings before merging code.
- **`cargo test`**: Write unit and integration tests for all logic.
- **`cargo doc`**: Generate documentation from doc comments. All public APIs MUST be documented.

## 8. Documentation
- **Doc Comments**: Use `///` for documenting public items (functions, structs, enums, modules).
- **Examples**: Include runnable examples in your documentation to demonstrate usage.
```rust
/// Represents a user in the system.
pub struct User {
    pub id: i32,
    pub email: String,
}

/// Fetches a user by their ID.
///
/// # Errors
///
/// Returns `Err` if the user is not found or if there is a database error.
///
/// # Example
///
/// ```
/// let user = get_user(1).await?;
/// ```
pub async fn get_user(id: i32) -> Result<User, MyError> {
    // ...
}
