import argparse
from subprocess import call


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

    args = parser.parse_args()

    app_name = args.app

    if args.build or args.full:
        call(
            f"docker build -f ./{app_name}_service.Dockerfile ./ -t {app_name}-service",
            shell=True
        )
    if args.push or args.full:
        call(f"""aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 802027775118.dkr.ecr.ap-south-1.amazonaws.com
        docker tag {app_name}-service:latest 802027775118.dkr.ecr.ap-south-1.amazonaws.com/{app_name}-service:latest
        docker push 802027775118.dkr.ecr.ap-south-1.amazonaws.com/{app_name}-service:latest
        """, shell=True)


if __name__ == "__main__":
    main()
