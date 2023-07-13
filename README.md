<h1 align="center">
    MindGPT &#129504;
</h1>

<p align="center">
    <a href="https://github.com/fuzzylabs/MindGPT/actions/workflows/ci.yml">
        <img alt="Build" src="https://img.shields.io/github/actions/workflow/status/fuzzylabs/MindGPT/ci.yml">
    </a>
    <a href="https://github.com/fuzzylabs/MindGPT/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/github/license/fuzzylabs/MindGPT?color=blue">
    </a>
</p>

MindGPT is a conversational system where users can ask mental health-orientated questions and receive answers which summarises content from two leading mental health websites: [Mind](https://www.mind.org.uk/) and [NHS Mental Health](https://www.nhs.uk/mental-health/).

**It's not a digital counsellor or therapist and the output from the system should not be treated as such**, MindGPT is purely focused on acting as a gateway to vital information sources, summarising two authoritative perspectives and providing pointers to the original content.

In building this, we've drawn on our expertise in MLOps and prior experience in fine-tuning open-source LLMs for various tasks (see [here](https://github.com/fuzzylabs/matcha-examples/tree/main/llm) for an example of one tuned to summarise legal text). If you're interested in how MindGPT works under the hood and what technologies and data we've used, then take a look [here](docs/inside-mindgpt.md).

# &#8265; Why?

Mental health problems are something that everyone struggles with at various points in their life and finding the right type of help and information can be hard, even a blocker. [Mind](https://www.mind.org.uk/), one of the main mental health charities in the UK, puts this best: _when you're living with a mental health problem, or support someone who is, having access to the right information is vital_.

MindGPT sets out to increase ease of access to this information.

# &#128064; Follow along

This project is in active development at Fuzzy Labs and you can follow along!

The repository for this project is one method where you can monitor progress - we're always raising pull requests to move the project forward. Another way you can do this is to follow our blog. We'll be posting periodic updates as we tick off sections of the project. If you're new to the project, the best place to start is our [project introduction](https://www.fuzzylabs.ai/blog-post/mindgpt-an-introduction).

# &#127939; How do I get started?

## Deployment pipeline

To run the zenml deployment pipeline, the resources required by seldon have to provisioned. `matcha` tool can help you in provisioning these resources.

Install `matcha-ml` library and provision resources using the same

```bash
pip install matcha-ml
matcha provision
```

After the provisioning completes, run the following bash script

```bash
./setup_deploy.sh
```

Run the deployment pipeline.

```bash
python run.py -d
```

You can take a look [here](docs/data-version-control.md) for guidance on interacting with data version control on this project.

## Streamlit Application

Once the deployment has completed, run the following command to start a streamlit application.

```bash
streamlit run app/app.py
```

# &#129309; Acknowledgements

This project wouldn't be possible without the exceptional content on both the Mind and NHS Mental Health websites.

# &#128220; License

This project is released under the Apache License. See [LICENSE](LICENSE).
