import uvicorn


def main() -> None:
    """Run the development server with reload enabled."""

    uvicorn.run(
        "documentation_digester.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
