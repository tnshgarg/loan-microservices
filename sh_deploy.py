import argparse
from subprocess import call
from datetime import date


def main():
    parser = argparse.ArgumentParser(description="A deployment helper for the microservices repo",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-a", "--app",
                        help="name of the app to build")
    parser.add_argument("-b", "--build", action="store_true",
                        help="flag to determine wether to build new image")
    parser.add_argument("-p", "--push", action="store_true",
                        help="flag to determine wether to push image to ecr")
    parser.add_argument("-f", "--full", action="store_true",
                        help="full deployment of build + push")
    parser.add_argument("-P", "--prod", action="store_true",
                        help="add a prod tag to for the built image")
    parser.add_argument("-Q", "--qa", action="store_true",
                        help="add a qa tag to for the built image")

    args = parser.parse_args()

    app_name = args.app

    if args.build or args.full:
        call(
            f"docker build -f ./{app_name}_service.Dockerfile ./ -t {app_name}-service",
            shell=True
        )
    if args.push or args.full:
        tag_name = "latest"
        if args.prod:
            tag_name = f"prod-{date.today()}"
        if args.qa:
            tag_name = f"qa-{date.today()}"
        call(f"""aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 802027775118.dkr.ecr.ap-south-1.amazonaws.com
        docker tag {app_name}-service:latest 802027775118.dkr.ecr.ap-south-1.amazonaws.com/{app_name}-service:{tag_name}
        docker push 802027775118.dkr.ecr.ap-south-1.amazonaws.com/{app_name}-service:{tag_name}
        """, shell=True)
        print(
            f"pushed tag: 802027775118.dkr.ecr.ap-south-1.amazonaws.com/{app_name}-service:{tag_name}"
        )


if __name__ == "__main__":
    main()
