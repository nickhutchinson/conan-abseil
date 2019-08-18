#!/usr/bin/env python3
import os
import pkg_resources
import sys

from cpt.packager import ConanMultiPackager

HERE = os.path.abspath(os.path.dirname(__file__))


def _add_cpp_stds(configs):
    ret = []
    for config in configs:
        cppstds = [
            arg.strip()
            for arg in os.environ.get("_XCONAN_CPPSTD", "default").split(",")
        ]

        for cppstd in cppstds:
            if cppstd == "default":
                ret.append(config)
            else:
                ret.append(
                    config._replace(
                        settings={**config.settings, "compiler.cppstd": cppstd}
                    )
                )

    return ret


def _add_macos_versions(configs):
    ret = []
    for config in configs:
        versions = [
            arg.strip()
            for arg in os.environ.get("_XCONAN_MACOS_VERSIONS", "default").split(",")
        ]

        for os_version in versions:
            if os_version == "default":
                ret.append(config)
            else:
                ret.append(
                    config._replace(
                        settings={**config.settings, "os.version": os_version}
                    )
                )

    return ret


def main():
    with open(os.path.join(HERE, "requirements.txt")) as f:
        requirement_str = f.read().replace("\\\n", " ").replace("\\\r\n", " ")

    reqs = [str(req) for req in pkg_resources.parse_requirements(requirement_str)]

    builder = ConanMultiPackager(pip_install=reqs)
    builder.add_common_builds(pure_c=False)

    configs = list(builder.items)
    configs = _add_cpp_stds(configs)

    if sys.platform == "darwin":
        configs = _add_macos_versions(configs)

    builder.items = configs
    builder.run()


if __name__ == "__main__":
    main()
