from setuptools import setup, find_packages

setup(
    name="trafficForecasting",
    version="0.0.5",
    packages=find_packages(exclude=["tests.*", "tests"]),
    description="Predict the Traffic",
    install_requires=["ricxappframe>=1.1.1,<2.0.0", "joblib>=0.3.2", "mdclogpy<=1.1.1", "influxdb", "pandas>=1.1.3", "scikit-learn", "schedule", "joblib","tensorflow"],
    entry_points={"console_scripts": ["run-qp.py=src.main:start"]},
    license="Apache 2.0",
    data_files=[("", ["LICENSE"])],
)
