# wikimedia-discord-embed

**As of early June 2026 embeds appear to be fixed.**

Simple Discord bot that replaces the functionality of native Wikimedia Commons embeds which have been broken since early January 2026.

When a message contains a direct Wikimedia Commons link the bot retrieves the image and posts it while removing the native embed from the source message.

Native embeds appear to be broken due to Wikimedia restricting clients that do not provide a conventional `User-Agent`. Photos retrieved prior to this change are cached and unaffected.

## Usage

The bot only requires the discord.py package available from pip. Set the `DISCORD_TOKEN` environment var and run the file.

## Techincal Notes

* Only URLs with the following scheme are recognized: `http[s]://commons.wikimedia.org/wiki/File:`
* There's a maximum of 10 images per message due to Discord restrictions.
* Filenames and the requesting user are listed alongside images.
* There's no error handling, raw Python errors get dumped to `stderr`.
* URLs do not require the scheme (e.g. `https`) to be recognized.

## License

This program is licensed under CC0-1.0, marked as dedicated to the public domain, see LICENSE file.

## Contributing

Please email any feedback or patches to [harry@harrystanton.com](mailto:harry@harrystanton.com), or submit a pull request in the project's [GitHub repository](https://github.com/harrystanton/wikimedia-discord-embed). I cherish all correspondence.
