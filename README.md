# Archives Backend
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor-ff69b4.svg)](CODE_OF_CONDUCT.md) [![Security](https://img.shields.io/badge/Security-Policy-green.svg)](SECURITY.md) [![Contributing](https://img.shields.io/badge/Contributing-Guidelines-blue.svg)](CONTRIBUTING.md)


This is the backend for the [Archives](https://archives.opendata.lk). It is a FastAPI application that serves the frontend and provides an API for the frontend to use.

## Features

| Feature | Description |
|---------|-------------|
| **Dashboard Statistics** | Real-time stats on document counts, availability, and temporal coverage. |
| **Advanced Search** | Metadata and text-based search with pagination and sorting. |
| **Graph Integration** | Explore relationships between documents via external Query API of [OpenGIN](https://github.com/LDFLK/OpenGIN). |
| **High Performance** | Asynchronous API with caching for dashboard stats. |
| **Lightweight Architecture** | Single-source-of-truth JSON metadata store replacing MongoDB. |
| **API Documentation** | Auto-generated interactive API docs by FastAPI. |


## Getting Started
Please see our [Getting Started Guide](GETTING_STARTED.md).
## Contributing
Please see our [Contributing Guide](CONTRIBUTING.md).
## Code of Conduct
Please see our [Code of Conduct](CODE_OF_CONDUCT.md).
## Security
Please see our [Security Policy](SECURITY.md).
## License
Distributed under the Apache 2.0 License. See [License](LICENSE) for more information.
## References
- Checkout our [Archives](https://archives.opendata.lk/) application. We serve this application using this service.
- Checkout our [Gztarchiver](https://github.com/LDFLK/gztarchiver) for more information. We use this tool to archive and gather information for this service.
- Checkout our [Archives Frontend](https://github.com/LDFLK/gztarchiver-ui-frontend) for more information. We use this service to serve this application.
---