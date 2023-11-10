from csv import DictWriter
from datetime import datetime, timedelta
import logging
from pathlib import Path
import shutil
from typing import Optional


from bgpy.caida_collector.graph import AS, BGPDAG

# Can't import into class due to mypy issue:
# https://github.com/python/mypy/issues/7045
# File funcs
from .file_reading_funcs import read_file
from .file_reading_funcs import _read_from_cache
from .file_reading_funcs import _read_from_caida
from .file_reading_funcs import _download_bz2_file
from .file_reading_funcs import _copy_to_cache

# HTML funcs
from .html_funcs import _get_url
from .html_funcs import _get_hrefs

# Graph building funcs
from .data_extraction_funcs import _get_ases
from .data_extraction_funcs import _extract_input_clique
from .data_extraction_funcs import _extract_ixp_ases
from .data_extraction_funcs import _extract_provider_customers
from .data_extraction_funcs import _extract_peers


class CaidaCollector:
    """Downloads relationships, determines metadata, and inserts to db"""

    read_file = read_file
    _read_from_cache = _read_from_cache
    _read_from_caida = _read_from_caida
    _download_bz2_file = _download_bz2_file
    _copy_to_cache = _copy_to_cache

    # HTML funcs
    _get_url = _get_url
    _get_hrefs = _get_hrefs

    # Graph building funcs
    _get_ases = _get_ases
    _extract_input_clique = _extract_input_clique
    _extract_ixp_ases = _extract_ixp_ases
    _extract_provider_customers = _extract_provider_customers
    _extract_peers = _extract_peers

    def __init__(self, BaseASCls: type[AS] = AS, GraphCls: type[BGPDAG] = BGPDAG):
        # Base AS Class for the BGPDAG
        self.BaseASCls: type[AS] = BaseASCls
        # BGPDAG class
        self.GraphCls: type[BGPDAG] = GraphCls

    def run(
        self,
        dl_time: Optional[datetime] = None,
        cache_dir: Path = Path("/tmp/caida_collector_cache"),
        tsv_path: Optional[Path] = Path("/tmp/caida_collector.tsv"),
    ):
        """Runs run func and deletes cache if anything is amiss"""

        try:
            return self._run(dl_time, cache_dir, tsv_path)
        except Exception as e:
            logging.critical(
                f"{e}: Potentially the result of a messed up"
                "cache, which was just deleted. please try again"
            )
            # MAke sure no matter what don't create a messed up cache
            shutil.rmtree(cache_dir)
            raise

    def _run(
        self, dl_time_arg: Optional[datetime], cache_dir: Path, tsv_path: Optional[Path]
    ) -> BGPDAG:
        """Downloads relationships, parses data, and inserts into the db.

        https://publicdata.caida.org/datasets/as-relationships/serial-2/

        Can specify a download time if you want to download an older dataset
        if cache is True it uses the downloaded file that was cached
        """

        # Get the download time
        if dl_time_arg:
            dl_time: datetime = dl_time_arg
        else:
            dl_time = self.default_dl_time()

        if cache_dir:
            # Make cache dir if cache is being used
            cache_dir.mkdir(parents=True, exist_ok=True)
            # Path to the cache file for that day
            fmt = "%Y.%m.%d"
            cache_path: Optional[Path] = cache_dir / dl_time.strftime(fmt)
        else:
            cache_path = None

        file_lines: tuple[str, ...] = self.read_file(cache_path, dl_time)
        (cp_links, peer_links, ixps, input_clique) = self._get_ases(file_lines)
        bgp_dag: BGPDAG = self.GraphCls(
            cp_links,
            peer_links,
            ixps=ixps,
            input_clique=input_clique,
            BaseASCls=self.BaseASCls,
        )
        if tsv_path:
            self._write_tsv(bgp_dag, tsv_path)

        return bgp_dag

    def default_dl_time(self) -> datetime:
        """Returns default DL time.

        For most things, we download from 4 days ago
        And for collectors, time must be divisible by 4/8
        """

        # 10 days because sometimes caida takes a while to upload
        # 7 days ago was actually not enough
        dl_time: datetime = datetime.utcnow() - timedelta(days=10)
        return dl_time.replace(hour=0, minute=0, second=0, microsecond=0)

    def _write_tsv(self, dag: BGPDAG, tsv_path: Path):
        """Writes BGP DAG info to a TSV"""

        logging.info("Made graph. Now writing to TSV")
        with tsv_path.open(mode="w") as f:
            # Get columns
            cols: list[str] = list(next(iter(dag.as_dict.values())).db_row.keys())
            writer = DictWriter(f, fieldnames=cols, delimiter="\t")
            writer.writeheader()
            for x in dag.as_dict.values():
                writer.writerow(x.db_row)
        logging.debug("Wrote TSV")
