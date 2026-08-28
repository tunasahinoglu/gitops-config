from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.gitops import ArgoCD
from diagrams.onprem.container import Docker
from diagrams.onprem.client import User
from diagrams.onprem.security import Trivy
from diagrams.aws.compute import ECR, EKS
from diagrams.aws.network import ELB
from diagrams.generic.compute import Rack

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.3",
    "splines": "spline",
    "nodesep": "0.5",
    "ranksep": "0.5",
}

with Diagram(
    "GitOps Deployment Pipeline",
    filename="architecture",
    outformat="png",
    direction="LR",
    graph_attr=graph_attr,
    show=False,
):
    dev = User("Developer")
    app_repo = Github("gitops-app")

    with Cluster("CI (GitHub Actions)"):
        test = GithubActions("Test, Lint,\nSonarQube Gate")
        build = Docker("Build Images")
        scan = Trivy("Trivy Scan")
        test >> build >> scan

    ecr = ECR("ECR\n(app + db images)")
    sonarqube = Rack("SonarQube")
    config_repo = Github("gitops-config\n(Helm + ArgoCD)")

    with Cluster("EKS Cluster (via gitops-infra)"):
        argocd = ArgoCD("ArgoCD")

        with Cluster("accounts namespace"):
            app_pod = Docker("app")
            db_pod = Docker("db")
            cache_pod = Docker("cache")
            mq_pod = Docker("mq")

    alb = ELB("ALB")
    user = User("User")

    dev >> Edge(label="push") >> app_repo
    app_repo >> Edge(label="triggers") >> test
    test >> Edge(label="analyze", style="dashed") >> sonarqube
    scan >> Edge(label="push image") >> ecr
    scan >> Edge(label="commit tag", style="dashed") >> config_repo
    config_repo >> Edge(label="pull & sync", style="dashed") >> argocd
    argocd >> Edge(style="dashed") >> app_pod
    argocd >> Edge(style="dashed") >> db_pod
    argocd >> Edge(style="dashed") >> cache_pod
    argocd >> Edge(style="dashed") >> mq_pod
    ecr >> Edge(label="pull image") >> app_pod
    ecr >> Edge(label="pull image") >> db_pod
    app_pod >> alb >> user