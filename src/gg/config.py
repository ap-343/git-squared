import toml

# Load the TOML file
config = toml.load("~/.config/git-squared/config.toml")

print(config)
