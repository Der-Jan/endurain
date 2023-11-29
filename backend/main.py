from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from controllers import (
    sessionController,
    userController,
    gearController,
    activitiesController,
    stravaController,
)
from datetime import datetime, timedelta

# from opentelemetry import trace
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# from dotenv import load_dotenv
import logging

# import os

app = FastAPI()

# load_dotenv("config/.env")

logger = logging.getLogger("myLogger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Configure Jaeger Exporter
# jaeger_exporter = JaegerExporter(
#    agent_host_name=os.getenv("JAEGER_HOST"),  # Update with your Jaeger host
#    agent_port=6831,  # Update with your Jaeger port
# )

# Create a TracerProvider with Jaeger exporter
# tracer_provider = TracerProvider(
#    resource=Resource.create({"service.name": "gearguardian-api"})
# )
# trace.set_tracer_provider(tracer_provider)
# tracer_provider.add_span_processor(SimpleSpanProcessor(jaeger_exporter))

# trace.set_tracer_provider(TracerProvider(resource=Resource.create().add_attribute("service.name", "backend_api")))
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({"service.name": "backend_api"}))
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://192.168.2.80:4317"))
)


# Instrument FastAPI app
FastAPIInstrumentor.instrument_app(app)

# Router files
app.include_router(sessionController.router)
app.include_router(userController.router)
app.include_router(gearController.router)
app.include_router(activitiesController.router)
app.include_router(stravaController.router)

# Create a background scheduler instance
scheduler = BackgroundScheduler()
scheduler.start()

# Remove the leading space
scheduler.add_job(sessionController.remove_expired_tokens, "interval", minutes=5)
scheduler.add_job(stravaController.refresh_strava_token, "interval", minutes=30)
scheduler.add_job(
    lambda: stravaController.get_strava_activities(
        (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ),
    "interval",
    minutes=60,
)


@app.on_event("startup")
async def startup_event():
    # Get the tracer
    tracer = trace.get_tracer(__name__)

    # Start a span for the startup event
    with tracer.start_as_current_span("startup_event"):
        print("Backend started!")


# Add the background scheduler to the app's shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    # Get the tracer
    tracer = trace.get_tracer(__name__)

    # Start a span for the startup event
    with tracer.start_as_current_span("shutdown_event"):
        scheduler.shutdown()