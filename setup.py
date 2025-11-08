from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='docufiller',
    version='1.0.0',
    author='DocuFiller Team',
    description='Intelligent document filling system with LLM-powered field mapping',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/docufiller',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Office/Business',
        'Topic :: Text Processing',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    keywords='document automation filling pdf docx llm ocr',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/docufiller/issues',
        'Source': 'https://github.com/yourusername/docufiller',
    },
)
