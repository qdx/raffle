# -*- coding: utf-8 -*-

import click

@click.command()
def main():
    """Raffle!!"""
    click.echo("Raffle system loading...")
    names = []
    with open("./data.txt", "r") as f:
        for n in f.readlines():
            names.append(n.strip())

    click.echo(f"{len(names)} users loaded, they are:")
    click.echo(names)

if __name__ == '__main__':
    main()
