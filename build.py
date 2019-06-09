#!/usr/bin/env python3
import os
import pkg_resources

from cpt.packager import ConanMultiPackager

HERE = os.path.abspath(os.path.dirname(__file__))


def main():
    with open(os.path.join(HERE, "requirements.txt")) as f:
        requirement_str = f.read().replace("\\\n", " ").replace("\\\r\n", " ")

    reqs = [str(req) for req in pkg_resources.parse_requirements(requirement_str)]

    builder = ConanMultiPackager(pip_install=reqs)
    builder.add_common_builds(pure_c=False)

    configs = []
    for config in builder.items:
        cppstds = [
            arg.strip()
            for arg in os.environ.get("_XCONAN_CPPSTD", "default").split(",")
        ]

        for cppstd in cppstds:
            if cppstd == "default":
                configs.append(config)
            else:
                configs.append(
                    config._replace(
                        settings={**config.settings, "compiler.cppstd": cppstd}
                    )
                )

    builder.items = configs
    builder.run()


if __name__ == "__main__":
    main()
