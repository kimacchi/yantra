"""Dockerfile template definitions for popular programming languages."""

LANGUAGE_TEMPLATES = [
    {
        "id": "python-3.12",
        "name": "Python 3.12",
        "description": "Latest Python 3.12 runtime with pip package manager. Ideal for modern Python development and data science.",
        "category": "language",
        "dockerfile_template": """FROM python:3.12-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["python", "-"]""",
        "default_run_command": ["python", "-"],
        "tags": ["python", "python3", "scripting"],
        "icon": "🐍",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "python-3.11-data",
        "name": "Python 3.11 Data Science",
        "description": "Python 3.11 with numpy, pandas, and matplotlib pre-installed for data science workloads.",
        "category": "language",
        "dockerfile_template": """FROM python:3.11-slim
WORKDIR /sandbox
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc g++ && \\
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy pandas matplotlib scipy
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["python", "-"]""",
        "default_run_command": ["python", "-"],
        "tags": ["python", "data-science", "numpy", "pandas"],
        "icon": "📊",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "nodejs-20",
        "name": "Node.js 20 LTS",
        "description": "Node.js 20 LTS with npm. Perfect for JavaScript server-side applications and scripts.",
        "category": "language",
        "dockerfile_template": """FROM node:20-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["node", "-"]""",
        "default_run_command": ["node", "-"],
        "tags": ["nodejs", "javascript", "node", "js"],
        "icon": "🟢",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "nodejs-18",
        "name": "Node.js 18 LTS",
        "description": "Node.js 18 LTS with npm. Stable long-term support version for production workloads.",
        "category": "language",
        "dockerfile_template": """FROM node:18-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["node", "-"]""",
        "default_run_command": ["node", "-"],
        "tags": ["nodejs", "javascript", "node", "js"],
        "icon": "🟢",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "typescript-5",
        "name": "TypeScript 5",
        "description": "TypeScript 5 with ts-node for direct TypeScript execution without pre-compilation.",
        "category": "language",
        "dockerfile_template": """FROM node:20-slim
WORKDIR /sandbox
RUN npm install -g typescript ts-node
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["ts-node"]""",
        "default_run_command": ["ts-node"],
        "tags": ["typescript", "ts", "node", "javascript"],
        "icon": "🔷",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "go-1.22",
        "name": "Go 1.22",
        "description": "Go 1.22 compiler and runtime. Fast compilation and execution for Go programs.",
        "category": "language",
        "dockerfile_template": """FROM golang:1.22-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
ENV CGO_ENABLED=0
CMD ["go", "run", "/dev/stdin"]""",
        "default_run_command": ["go", "run", "/dev/stdin"],
        "tags": ["go", "golang", "compiled"],
        "icon": "🐹",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "rust-stable",
        "name": "Rust Stable",
        "description": "Rust stable toolchain with cargo. Modern systems programming with memory safety.",
        "category": "language",
        "dockerfile_template": """FROM rust:slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
# Note: Rust code needs to be in a proper project structure for compilation
CMD ["rustc", "-"]""",
        "default_run_command": ["rustc", "-"],
        "tags": ["rust", "systems", "compiled"],
        "icon": "🦀",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "java-21",
        "name": "Java 21 LTS",
        "description": "OpenJDK 21 LTS with modern Java features. Long-term support version for enterprise applications.",
        "category": "language",
        "dockerfile_template": """FROM eclipse-temurin:21-jdk-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["jshell"]""",
        "default_run_command": ["jshell"],
        "tags": ["java", "jvm", "jdk"],
        "icon": "☕",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "java-17",
        "name": "Java 17 LTS",
        "description": "OpenJDK 17 LTS. Previous LTS version, widely used in production environments.",
        "category": "language",
        "dockerfile_template": """FROM eclipse-temurin:17-jdk-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["jshell"]""",
        "default_run_command": ["jshell"],
        "tags": ["java", "jvm", "jdk"],
        "icon": "☕",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "dotnet-8",
        "name": ".NET 8",
        "description": ".NET 8 SDK with C# support. Modern cross-platform development with Microsoft's latest framework.",
        "category": "language",
        "dockerfile_template": """FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["dotnet", "script"]""",
        "default_run_command": ["dotnet", "script"],
        "tags": ["csharp", "dotnet", "c#", "microsoft"],
        "icon": "💜",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "php-8.3",
        "name": "PHP 8.3",
        "description": "PHP 8.3 with CLI and Composer. Latest PHP version with modern language features.",
        "category": "language",
        "dockerfile_template": """FROM php:8.3-cli-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
USER sandbox
CMD ["php", "-a"]""",
        "default_run_command": ["php", "-a"],
        "tags": ["php", "web", "scripting"],
        "icon": "🐘",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "php-8.2",
        "name": "PHP 8.2",
        "description": "PHP 8.2 with CLI and Composer. Stable PHP version with excellent performance.",
        "category": "language",
        "dockerfile_template": """FROM php:8.2-cli-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
USER sandbox
CMD ["php", "-a"]""",
        "default_run_command": ["php", "-a"],
        "tags": ["php", "web", "scripting"],
        "icon": "🐘",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "gcc-latest",
        "name": "GCC C/C++",
        "description": "GCC compiler for C and C++ with standard libraries. Supports C11, C++17, and C++20.",
        "category": "language",
        "dockerfile_template": """FROM gcc:latest
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
# For C: gcc -x c -o /tmp/program - && /tmp/program
# For C++: g++ -x c++ -o /tmp/program - && /tmp/program
CMD ["gcc", "--version"]""",
        "default_run_command": ["gcc", "-x", "c", "-o", "/tmp/program", "-", "&&", "/tmp/program"],
        "tags": ["c", "cpp", "c++", "gcc", "compiled"],
        "icon": "⚙️",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "ruby-3.3",
        "name": "Ruby 3.3",
        "description": "Ruby 3.3 with gem package manager. Modern Ruby for scripting and web applications.",
        "category": "language",
        "dockerfile_template": """FROM ruby:3.3-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["ruby"]""",
        "default_run_command": ["ruby"],
        "tags": ["ruby", "scripting", "rails"],
        "icon": "💎",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "perl-5",
        "name": "Perl 5",
        "description": "Perl 5 interpreter with CPAN. Classic scripting language for text processing.",
        "category": "language",
        "dockerfile_template": """FROM perl:slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["perl"]""",
        "default_run_command": ["perl"],
        "tags": ["perl", "scripting"],
        "icon": "🐪",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "r-4",
        "name": "R 4",
        "description": "R language for statistical computing with base packages. Ideal for data analysis and visualization.",
        "category": "language",
        "dockerfile_template": """FROM r-base:latest
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["R", "--vanilla"]""",
        "default_run_command": ["R", "--vanilla"],
        "tags": ["r", "statistics", "data-science"],
        "icon": "📈",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "lua-5.4",
        "name": "Lua 5.4",
        "description": "Lua 5.4 interpreter. Lightweight scripting language often used in embedded systems and games.",
        "category": "language",
        "dockerfile_template": """FROM alpine:latest
WORKDIR /sandbox
RUN apk add --no-cache lua5.4
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["lua5.4"]""",
        "default_run_command": ["lua5.4"],
        "tags": ["lua", "scripting", "embedded"],
        "icon": "🌙",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "swift-5",
        "name": "Swift 5",
        "description": "Swift 5 compiler and runtime. Apple's modern programming language for iOS, macOS, and server-side development.",
        "category": "language",
        "dockerfile_template": """FROM swift:latest
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["swift"]""",
        "default_run_command": ["swift"],
        "tags": ["swift", "apple", "ios"],
        "icon": "🦅",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "kotlin-jvm",
        "name": "Kotlin JVM",
        "description": "Kotlin compiler for JVM. Modern language with Java interoperability and null safety.",
        "category": "language",
        "dockerfile_template": """FROM eclipse-temurin:21-jdk-alpine
WORKDIR /sandbox
RUN apk add --no-cache wget unzip && \\
    wget -q https://github.com/JetBrains/kotlin/releases/download/v1.9.22/kotlin-compiler-1.9.22.zip && \\
    unzip -q kotlin-compiler-1.9.22.zip && \\
    mv kotlinc /opt/ && \\
    rm kotlin-compiler-1.9.22.zip && \\
    apk del wget unzip
ENV PATH="/opt/kotlinc/bin:${PATH}"
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["kotlinc"]""",
        "default_run_command": ["kotlinc"],
        "tags": ["kotlin", "jvm", "android"],
        "icon": "🎯",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "scala-3",
        "name": "Scala 3",
        "description": "Scala 3 compiler and runtime. Modern functional and object-oriented programming on the JVM.",
        "category": "language",
        "dockerfile_template": """FROM hseeberger/scala-sbt:eclipse-temurin-21.0.1_12_1.9.8_3.3.1
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["scala"]""",
        "default_run_command": ["scala"],
        "tags": ["scala", "jvm", "functional"],
        "icon": "🔴",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "elixir-1.16",
        "name": "Elixir 1.16",
        "description": "Elixir 1.16 on Erlang VM. Functional language for scalable and maintainable applications.",
        "category": "language",
        "dockerfile_template": """FROM elixir:1.16-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["iex"]""",
        "default_run_command": ["iex"],
        "tags": ["elixir", "erlang", "functional", "beam"],
        "icon": "💧",
        "author": "yantra",
        "is_official": True,
    },
    {
        "id": "haskell-9",
        "name": "Haskell 9",
        "description": "Haskell 9 with GHC compiler. Pure functional programming with strong type system.",
        "category": "language",
        "dockerfile_template": """FROM haskell:9-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["ghci"]""",
        "default_run_command": ["ghci"],
        "tags": ["haskell", "functional", "pure"],
        "icon": "λ",
        "author": "yantra",
        "is_official": True,
    },
]
