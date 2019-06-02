import os
import pkg_resources

from cpt.packager import ConanMultiPackager

HERE = os.path.abspath(os.path.dirname(__file__))


def main():
    with open(os.path.join(HERE, "requirements.txt")) as f:
        requirement_str = f.read().replace("\\\n", " ").replace("\\\r\n", "")

    reqs = [str(req) for req in pkg_resources.parse_requirements(requirement_str)]

    builder = ConanMultiPackager(pip_install=reqs)
    builder.add_common_builds(pure_c=False)

    configs = []
    for config in builder.items:
        cxx_stds = [
            arg.strip()
            for arg in os.environ.get("ABSEIL_CXX_STD", "default").split(",")
        ]

        for cxx_std in cxx_stds:
            if cxx_std == "default":
                configs.append(config)
            else:
                configs.append(
                    config._replace(options={**config.options, "cxx_std": cxx_std})
                )

    builder.items = configs
    builder.run()


if __name__ == "__main__":
    main()
