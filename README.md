[![Test Application](https://github.com/braboj/randomgen/actions/workflows/test_application.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/test_application.yml)
[![Deploy Image](https://github.com/braboj/randomgen/actions/workflows/deploy_image.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/deploy_image.yml)
[![Deploy Pages](https://github.com/braboj/randomgen/actions/workflows/deploy_pages.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/deploy_pages.yml)

# Overview

This project provides a simple REST API for generating random numbers. It is built using Python and the Flask framework. The application is packaged as a Docker image, making it easy to run on any platform that supports Docker.

# Installation

To get started, you need to install Docker. You can find the installation
instructions [here](https://docs.docker.com/engine/install/). After that, 
you can run the following command to get the project image:

```bash
docker pull braboj/randomgen:latest
```

And finally, you can run the following command to start the project:

```bash
docker run -p 5000:5000 braboj/randomgen:latest
```

To access the project, open your browser and go to 
[http://localhost:5000](http://localhost:5000). A simple page will be 
displayed with the endpoints available. As a quick example, use the 
following link to create 100 random numbers:

```text
http://localhost:5000/api/v1/randomgen?numbers=100
```

# Next Steps
 - For more information, you can check [RandomGen Project Pages](https://braboj.github.io/randomgen/).
 - To contribute, please visit [Contributing](CONTRIBUTING.md)
 - To leave feedback, please visit [Discussions](https://github.com/braboj/randomgen/discussions/landing)
