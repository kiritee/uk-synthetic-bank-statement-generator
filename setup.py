from setuptools import setup

setup(
    name='bankgen',
    version='0.1',
    py_modules=['bankgen'],
    packages=['scripts'],
    install_requires=[
        'openai', 'pandas', 'tqdm', 'pyyaml', 'tenacity'
    ],
    entry_points={
        'console_scripts': [
            'bankgen = bankgen:main',
        ],
    },
)
