# Todo

Todo is an example application intended to illustrate the scaffolding
and developer tooling necessary to support effective development of a
microservices application.

This application uses kubernetes and envoy as foundational
technologies, as well as forge, telepresence, and ambassador to
provide a productive developer workflows on top of these tools.

If you are trying to bootstrap a microservices application, you can
use this as a starter kit and plug in your own services. If you
already have one, you can pick apart what you like from this and
ignore or adapt the rest.

The application consists of 4 services:

  - A tasks service (currently a stub) but notionally responsible for
    remembering whatever tasks a user might want to do.

  - A search service (currently a stub) but notionally responsible
    enabling users to find particular tasks on demand.

  - An API gateway service that uses envoy + ambassador to provide L7
    routing, traffic splitting (for canary releases), and
    authentication.

  - An authentication service that (via the ambassador plugin)
    provides custom authentication logic in a single edge service. The
    authentication service provide delegates to auth0.

Service Topology:

![alt text](docs/topology.png "Service Topology Diagram")

This application provides a working example to illustrate all of the
following:

1. How to do authentication with microservices.

2. How to provide a fast dev/prototype experience (REPL) with
   microservices.

3. How to run tests with microservices.

4. How to quickly and easily deploy the entire application (or a
   subset of it) into different environments (shared dev, staging,
   prod, personal dev environments, isolated testing environments).

5. How to do canary deploys.

## Directory layout:

This application is layed out as a monorepo for convenience, however
each service directory is independently releasable, and all the
tooling provided will work seamlessly with a one repo per service
layout.

```
 <root>
   |
   |               API Gateway
   |
   +--- service.yaml        (service metadata for forge)
   |
   +--- Dockerfile          (dockerfile that builds the API Gateway)
   |
   +--- envoy.json          (configuration file for the API gateway)
   |
   +--- k8s/deployment.yaml (deployment templates for the API gateway)
   |
   |
   +--- auth                  Authentication Service
   |     |
   |     +--- service.yaml        (service metadata for forge)
   |     |
   |     +--- Dockerfile          (dockerfile that builds the authentication service)
   |     |
   |     +--- k8s/deployment.yaml (deployment templates for the auth service)
   |     |
   |     +--- *                   (auth service implementation)
   |     
   |
   +--- tasks                 Tasks Service
   |     |
   |     +--- service.yaml        (service metadata for forge)
   |     |
   |     +--- Dockerfile          (dockerfile that builds the tasks service)
   |     |
   |     +--- k8s/deployment.yaml (deployment templates for the tasks service)
   |     |
   |     +--- *                   (task service implementation)
   |
   |
   +--- search                 Search Service
   |     |
   |     +--- service.yaml        (service metadata for forge)
   |     |
   |     +--- Dockerfile          (dockerfile that builds the search service)
   |     |
   |     +--- k8s/deployment.yaml (deployment templates for the search service)
   |     |
   |     +--- *                   (task service implementation)
   |
   |
   +--- ...
   |
   .
   .
```

## Standing up the application

You will need `kubectl`, `docker`, and [forge](http://forge.sh) to be
installed in order to follow these instructions:

1. Make sure your `kubectl` is configured to talk to the cluster into
   which you would like to deploy the application.

2. Clone this repository: `git clone ...`

3. Change into cloned repo directory: `cd todo`

4. Run `forge deploy`

Note, this last step is a bit of a wart/edge case and should be able
to go away at some point.

5. Change to the tasks directory and do a canary deploy of tasks:
   `cd tasks && CANARY=true forge deploy`

The reason this last step is necessary is because the tasks service
always has two deployments, the stable deployment, and the canary
deployment. The API gateway is configured to split traffic between
these two deployments in a 90%/10% proportion. If you have nothing to
canary, you simply deploy the stable code into the canary deployment
and the traffic still flows to both deployments, but each deployment
is running the same code.

This is simple to set up, and can be easily customized (even
dynamically) to split a different proportion of traffic depending on
what is appropriate for a given microservice, however this does
currently leave the bootstrapping wart of doing a 'noop' canary deploy
in order to avoid 10% of your traffic flowing to a nonexistent
deployment.

## Deploying a change

1. Edit any files you would like to change.

2. Run: `forge deploy`

This will redeploy any pieces necessary. Note that `forge deploy` will
figure out what services to operate on based on the current working
directory. If you want to deploy a change to just one service
(e.g. just the tasks service), cd into `tasks` and run `forge deploy`
from there.

## Deploying a canary

Note that only the tasks service is set up to enable canary
deployments. One of the benefits of independently releasable services,
is that you can use different workflows for different services, rapid
application development for new services with no users, and careful
canary releases for stable services with many users.

1. Change to the tasks directory: `cd tasks`

2. Change whatever you would like (code, deployment metadata, etc).

3. Run: `CANARY=true forge deploy`

This will push your change to the canary deployment for tasks, and now
10% of the traffic to the tasks service will hit your canary.

## Rationale

Microservices is not a technology, design, or architecture. It is
first and foremost a new way of building software.

This way of working has two main benefits. First it is particularly
well suited to improving continuous uptime systems *while* they are in
use.

Second, it is particularly well suited to dividing up the work of
building these systems amongst many autonomous fast-moving teams.

The technology that exists in this space did not enable this new way
of working, rather the reverse. A new way of working resulted in a
bunch of tools that help make it more efficient, but are not
ultimately necessary.

Most of the technology that has been open sourced, does not actually
illustrate the workflow (how it is used, and when it is appropriate to
use). This application is intended to fill that gap by illustrating
how you can put together productive workflows using foundational
microservices tech.
