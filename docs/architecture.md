# ProjectX-Ray Architecture

## Initial architecture

```text
Client / Frontend
       |
       v
FastAPI API
       |
       +--> Project analysis service
       +--> Risk scoring service
       +--> Recommendation service
```

The first milestone keeps the system modular and testable. Advanced models and external research components can be added after the deterministic MVP is working.
