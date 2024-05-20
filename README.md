# Better-nest, an AI Agent for Climate Control

[![Run Program](https://github.com/PatrickKalkman/better-nest/actions/workflows/run_program.yml/badge.svg)](https://github.com/PatrickKalkman/better-nest/actions/workflows/run_program.yml)

![AI Agent](cover.jpg)

This repository contains the code for the AI agent described in the [Medium article "AI Agent for Smart Home Climate Control: Harnessing Botanical Strategies for Energy Efficiency"](https://medium.com/@pkalkman) 

## Running the Agent

The complete source code for the AI agent is available in this repository. Below, you'll find step-by-step instructions for configuring and running the agent on your local machine.

While running the program might require specific environment settings, some of which involve creating accounts to access necessary APIs, a demo mode is available that allows you to run the agent using cached data. By default, this demo mode is enabled. You can change it via the `configuration_node` function in `config.py`.

### Configuration

To use live data instead of the demo mode, change the `mode` key in `configuration_node` to something other than "demo." Remember to set all the required environment variables as specified in the `.env.example` file.

### Installing dependencies

The program uses various PyPi packages. You can install these dependencies via pip or conda depending on your preference. Run the following command in your terminal to set up your environment:

#### Using Conda

Create a Conda environment from the provided `environment.yml` file:

```sh
conda env create -f environment.yml
```

#### Using Pip

```sh
pip install -r requirements.txt
```

### Starting the Agent

Once you’ve configured your environment and installed all dependencies, you can run the agent by executing the main script:

```sh
python main.py
```


### License

This project is licensed under the MIT License.