import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='vmcompact',
    version='0.0.1',
    author='Onyx and Iris',
    author_email='code@onyxandiris.online',
    description='Compact Tkinter Voicemeeter Remote App',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/onyx-and-iris/voicemeeter-compact',
    project_urls = {
        "Bug Tracker": "https://github.com/onyx-and-iris/voicemeeter-compact/issues"
    },
    license='MIT',
    packages=['vmcompact'],
    install_requires=[
        'toml',
        'voicemeeter@git+https://github.com/onyx-and-iris/voicemeeter-api-python#egg=voicemeeter',
        'vbancmd@git+https://github.com/onyx-and-iris/vban-cmd-python#egg=vbancmd',
    ],
)
