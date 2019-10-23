import configparser
import io
import os
from collections import defaultdict

import click

from .xav import AddressParseError, UpsXavBatch, UpsXavBatchAndLogger


def _get_ups_credentials(config=None):
    credentials = defaultdict(None)
    if config:
        parser = configparser.ConfigParser()
        parser.read(config)
        credentials = {
            "username": parser.get("ups", "username", fallback=None),
            "password": parser.get("ups", "password", fallback=None),
            "license": parser.get("ups", "license", fallback=None),
        }
    return credentials


@click.group()
@click.pass_context
@click.version_option()
@click.option(
    "--credentials",
    envvar="UPS_CREDENTIALS",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
def ups(ctx, credentials):
    ctx.ensure_object(dict)
    ctx.obj["credentials"] = _get_ups_credentials(credentials)


@ups.command()
@click.pass_context
@click.argument("address")
def xav(ctx, address):
    """Validate a street address using the UPS API.

    \b
    Examples
    --------
    $ ups xav "1600 Pennsylvania Avenue NW, Washington, DC, 20500"
    """
    validator = UpsXavBatch(**ctx.obj["credentials"])

    try:
        candidates = list(validator.post_all(io.StringIO(address)))[0]
    except AddressParseError as error:
        click.secho(str(error), fg="red", err=True)
    else:
        if len(candidates) == 0:
            click.secho("no candidates found", fg="yellow", err=True)
        else:
            click.secho(
                os.linesep.join([str(address) for address in candidates]), err=False
            )


@ups.command()
@click.pass_context
@click.argument("address_file", type=click.File("r"))
@click.option("--output", "-o", type=click.File("w"))
@click.option("--progress-bar", is_flag=True, flag_value=True)
@click.option("--log/--no-log", default=True)
def xav_batch(ctx, address_file, output, progress_bar, log):
    credentials = ctx.obj["credentials"]

    if log:
        validator = UpsXavBatchAndLogger(**credentials)
    else:
        validator = UpsXavBatch(**credentials)

    def stringify(index, addresses):
        return os.linesep.join(
            ["{0},{1}".format(index, str(address)) for address in addresses or [",,,"]]
        )

    addresses = validator.iter(address_file)
    if progress_bar:
        label = "🚀 {fname}".format(fname=os.path.basename(address_file.name))
        with click.progressbar(addresses, label=label) as bar:
            for index, candidates in enumerate(bar):
                click.secho(stringify(index, candidates), file=output)
    else:
        for index, candidates in enumerate(addresses):
            click.secho(stringify(index, candidates), file=output)

    click.secho(
        "💥 Finished. Processed {0} addresses ({1} warnings, {2} errors)".format(
            len(addresses), validator.warning, validator.error
        ),
        err=True,
        fg="green",
    )
