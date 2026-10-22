# 가상환경 설정: conda 환경 camp (python 3.12) 생성 후 활성화
# 사용법: PowerShell에서 .\setup_env.ps1
# 비활성화: conda deactivate

$envName = "camp"
$pythonVersion = "3.12"

# 스크립트 안에서 conda activate를 쓰려면 conda hook이 필요하다
(& conda "shell.powershell" "hook") | Out-String | Invoke-Expression

$exists = conda env list | Select-String -Pattern "^$envName\s"
if (-not $exists) {
    conda create -n $envName python=$pythonVersion -y
}

conda activate $envName
python --version
