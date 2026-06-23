# 12. Glossary

Domain and technical terms used across this documentation.

| Term | Definition |
|------|------------|
| **Discrete distribution** | A finite set of outcomes (numbers), each with a probability (probabilities). RandomGen draws from such a distribution; weights must be non-negative and sum to 1 (within rounding). |
| **Default distribution** | The built-in distribution used when none is supplied: DEFAULT_NUMBERS = [-1, 0, 1, 2, 3] with DEFAULT_PROBABILITIES = [0.01, 0.3, 0.58, 0.1, 0.01]. |
| **numbers (param)** | The quantity of random numbers to generate per request (default DEFAULT_QUANTITY = 1000, bounded 1..MAX_NUMBERS). Distinct from the distribution's outcomes. |
| **dist (param)** | Per-request distribution as comma-separated value:probability pairs (e.g. 1:0.5,2:0.5). Preferred override; takes precedence over value/probability. |
| **value / probability (params)** | Repeated, parallel per-request distribution parameters (legacy). Used only when dist is absent. |
| **MAX_NUMBERS** | Upper bound (10000) on the quantity generated per request. |
| **CDF (cumulative distribution function)** | Running sum of probabilities, precomputed by calc_cdf(). RandomGenV1 samples by inverse-CDF lookup. |
| **Inverse-CDF sampling** | RandomGenV1's method: draw random.random(), return the first outcome whose cumulative probability is >= rand. |
| **RandomGenV1** | Generator using manual inverse-CDF sampling over random.random(). Exposed at /api/v1/randomgen. |
| **RandomGenV2** | Generator using random.choices(numbers, probabilities). Exposed at /api/v2/randomgen. |
| **Histogram** | Observed-frequency distribution of a sample (Histogram, a dict subclass): each value mapped to its observed proportion. |
| **Chi-Square test** | Goodness-of-fit test (ChiSquareTest) comparing observed vs. expected frequencies; reports the statistic, degrees of freedom, and p-value (via scipy.stats.chi2). |
| **Null hypothesis / is_null** | The hypothesis that the observed sample matches the expected distribution. is_null is True when p_value > alpha (default α = 0.05). |
| **p-value** | Probability of observing a statistic at least as extreme under the null hypothesis: 1 - chi2.cdf(chi_square, df). |
| **Degrees of freedom (df)** | len(contributing categories) - 1 (probabilities are given, not estimated, so no extra reduction). |
| **RandomGenError** | Base class for all domain exceptions in domain/errors.py; mapped to HTTP 400 by the error handler. |
| **Application factory** | create_app() in app.py — builds and configures the Flask app (blueprint + error handler) once per process. |
| **Blueprint** | Flask's mechanism for grouping routes; a web blueprint plus one API blueprint per version (built from the registry) hold the route handlers. |
| **Stateless service** | RandomGenService — holds no mutable state, so one instance is shared safely across requests and gunicorn workers. |
| **gunicorn** | Production WSGI server that runs the app in the container (gunicorn 'randomgen.app:create_app()'). |
| **WSGI** | Web Server Gateway Interface — the Python standard between the web server (gunicorn) and the app (Flask). |
| **Werkzeug** | The WSGI/HTTP library Flask is built on; raises HTTPException subclasses (e.g. 404, 405) that the error handler maps to their own status. |
| **/health** | Liveness endpoint returning {"status":"ok"}; used by Docker HEALTHCHECK and Render. |
| **Digest pin** | Referencing the Docker base image by @sha256:… for a reproducible, integrity-checked build. |
| **Render blueprint** | render.yaml — declarative spec deploying the container as a free Render web service. |
| **gitleaks** | Secret-scanning tool run in CI (ci.yml) to prevent committing credentials. |
| **arc42** | The architecture documentation template used by this docs/arc42/ set ([arc42.org](https://arc42.org)). |
