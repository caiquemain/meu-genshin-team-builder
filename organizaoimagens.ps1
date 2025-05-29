# --- CONFIGURAÇÃO ---
$baseProjectPath = "C:\Projetos\meu-genshin-team-builder" # <<< AJUSTE A RAIZ DO SEU PROJETO SE NECESSÁRIO
$baseImagePath = Join-Path -Path $baseProjectPath -ChildPath "frontend\public\assets\images"

# Subpastas alvo dentro de $baseImagePath
$targetSubfolders = @(
    "characters",
    "elements",
    "weapons", # Para ícones de TIPOS de armas (filtros)
    "weapons_detail", # Para ícones de ARMAS ESPECÍFICAS (in-game)
    "artifact_sets", # Para ícones de CONJUNTOS de artefatos
    "rarity"
)

# --- CRIAÇÃO DAS SUBPASTAS ---
Write-Host "Verificando e criando subpastas em '$baseImagePath'..." -ForegroundColor Cyan
foreach ($folderName in $targetSubfolders) {
    $folderPath = Join-Path -Path $baseImagePath -ChildPath $folderName
    if (-not (Test-Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath | Out-Null
        Write-Host "Pasta criada: '$folderName'" -ForegroundColor Green
    }
}
Write-Host "------------------------------------"

# --- MAPEAMENTO E MOVIMENTAÇÃO DE IMAGENS ---
# Lista de imagens para mover e/ou renomear.
# CurrentImageName: Nome do arquivo como está AGORA, assumindo que está DIRETAMENTE em $baseImagePath.
# TargetImageName: NOVO nome do arquivo (idealmente minúsculo, com underscores se necessário, e .png).
# TargetSubfolder: Para qual das $targetSubfolders a imagem deve ser movida.

$imageMappings = @(
    # Personagens (Exemplos - Adicione todos os seus personagens)
    # Se o seu arquivo Albedo.png (maiúsculo) estava na raiz de 'images' e você quer movê-lo para 'characters/albedo.png'
    [pscustomobject]@{ CurrentImageName = "Albedo.png"; TargetImageName = "albedo.png"; TargetSubfolder = "characters" }
    [pscustomobject]@{ CurrentImageName = "Xiangling.png"; TargetImageName = "xiangling.png"; TargetSubfolder = "characters" }
    [pscustomobject]@{ CurrentImageName = "Varesa.png"; TargetImageName = "varesa.png"; TargetSubfolder = "characters" }
    # Adicione mais entradas para cada arquivo de personagem que precisa ser movido/renomeado
    # Ex: [pscustomobject]@{ CurrentImageName = "Hu Tao.png"; TargetImageName = "hu_tao.png"; TargetSubfolder = "characters" }
    # Ex: [pscustomobject]@{ CurrentImageName = "Traveler (Anemo).png"; TargetImageName = "traveler_anemo.png"; TargetSubfolder = "characters" }


    # Ícones de Elementos (se ainda estiverem na raiz de $baseImagePath)
    [pscustomobject]@{ CurrentImageName = "element_anemo.png"; TargetImageName = "element_anemo.png"; TargetSubfolder = "elements" }
    [pscustomobject]@{ CurrentImageName = "element_geo.png"; TargetImageName = "element_geo.png"; TargetSubfolder = "elements" }
    [pscustomobject]@{ CurrentImageName = "element_electro.png"; TargetImageName = "element_electro.png"; TargetSubfolder = "elements" }
    [pscustomobject]@{ CurrentImageName = "element_dendro.png"; TargetImageName = "element_dendro.png"; TargetSubfolder = "elements" }
    [pscustomobject]@{ CurrentImageName = "element_hydro.png"; TargetImageName = "element_hydro.png"; TargetSubfolder = "elements" }
    [pscustomobject]@{ CurrentImageName = "element_pyro.png"; TargetImageName = "element_pyro.png"; TargetSubfolder = "elements" }
    [pscustomobject]@{ CurrentImageName = "element_cryo.png"; TargetImageName = "element_cryo.png"; TargetSubfolder = "elements" }

    # Ícones de Tipos de Armas (para filtros, se estiverem na raiz de $baseImagePath)
    [pscustomobject]@{ CurrentImageName = "weapon_sword.png"; TargetImageName = "weapon_sword.png"; TargetSubfolder = "weapons" }
    [pscustomobject]@{ CurrentImageName = "weapon_claymore.png"; TargetImageName = "weapon_claymore.png"; TargetSubfolder = "weapons" }
    [pscustomobject]@{ CurrentImageName = "weapon_polearm.png"; TargetImageName = "weapon_polearm.png"; TargetSubfolder = "weapons" }
    [pscustomobject]@{ CurrentImageName = "weapon_bow.png"; TargetName = "weapon_bow.png"; TargetSubfolder = "weapons" }
    [pscustomobject]@{ CurrentImageName = "weapon_catalyst.png"; TargetImageName = "weapon_catalyst.png"; TargetSubfolder = "weapons" }

    # Ícones de Raridade (para filtros, se estiverem na raiz de $baseImagePath)
    [pscustomobject]@{ CurrentImageName = "rarity_4.png"; TargetImageName = "rarity_4.png"; TargetSubfolder = "rarity" }
    [pscustomobject]@{ CurrentImageName = "rarity_5.png"; TargetName = "rarity_5.png"; TargetSubfolder = "rarity" }

    # Ícones de Conjuntos de Artefatos (adicione os seus)
    # [pscustomobject]@{ CurrentImageName = "NomeAtualSetArtefato.png"; TargetImageName = "id_do_set.png"; TargetSubfolder = "artifact_sets" }

    # NOTA PARA ARMAS ESPECÍFICAS (weapons_detail):
    # A próxima seção do script trata de padronizar para minúsculas os arquivos que JÁ ESTÃO na pasta 'weapons_detail'.
    # Se você tiver ícones de armas específicas AINDA NA RAIZ de '$baseImagePath', adicione mapeamentos para elas aqui.
    # Ex: [pscustomobject]@{ CurrentImageName = "Amos_Bow_ImagemOriginal.png"; TargetImageName = "amos_bow.png"; TargetSubfolder = "weapons_detail" }
)

Write-Host "Processando mapeamentos de imagens..." -ForegroundColor Cyan
foreach ($map in $imageMappings) {
    $sourceFile = Join-Path -Path $baseImagePath -ChildPath $map.CurrentImageName
    $destinationDir = Join-Path -Path $baseImagePath -ChildPath $map.TargetSubfolder
    $destinationFile = Join-Path -Path $destinationDir -ChildPath $map.TargetImageName

    if (Test-Path $sourceFile) {
        try {
            # Garante que o diretório de destino da subpasta existe
            if (-not (Test-Path $destinationDir)) {
                New-Item -ItemType Directory -Path $destinationDir -ErrorAction Stop | Out-Null
            }
            Move-Item -Path $sourceFile -Destination $destinationFile -Force -ErrorAction Stop
            Write-Host "OK: '$($map.CurrentImageName)' movido/renomeado para '$($map.TargetSubfolder)\$($map.TargetImageName)'" -ForegroundColor Green
        }
        catch {
            Write-Host "ERRO ao processar '$($map.CurrentImageName)': $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        # Se o arquivo não está na raiz, talvez já tenha sido movido ou o nome está incorreto no mapeamento
        # Write-Host "AVISO: Arquivo de origem '$($map.CurrentImageName)' não encontrado em '$baseImagePath'. Pulando." -ForegroundColor Yellow
    }
}
Write-Host "------------------------------------"

# --- PADRONIZAR NOMES DE ARQUIVOS EM weapons_detail PARA MINÚSCULAS ---
# Esta seção assume que os arquivos de ícones de armas específicas já estão na pasta 'weapons_detail'
# e apenas garante que seus nomes estejam em minúsculas.
$weaponsDetailPath = Join-Path -Path $baseImagePath -ChildPath "weapons_detail"
if (Test-Path $weaponsDetailPath) {
    Write-Host "Padronizando nomes de arquivos em '$weaponsDetailPath' para minúsculas..." -ForegroundColor Cyan
    Get-ChildItem -Path $weaponsDetailPath -File -Filter *.png | ForEach-Object {
        $originalName = $_.Name
        $lowerCaseName = $originalName.ToLower()
        
        if ($originalName -cne $lowerCaseName) {
            # -cne é "case-sensitive not equal"
            $originalFullName = $_.FullName
            $newFullName = Join-Path -Path $_.DirectoryName -ChildPath $lowerCaseName
            try {
                Rename-Item -Path $originalFullName -NewName $lowerCaseName -ErrorAction Stop
                Write-Host "RENOMEADO (weapons_detail): '$originalName' para '$lowerCaseName'" -ForegroundColor Green
            }
            catch {
                Write-Host "ERRO ao renomear '$originalName' para '$lowerCaseName' em weapons_detail: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}
else {
    Write-Host "AVISO: Pasta '$weaponsDetailPath' não encontrada. Pulando padronização de nomes de armas." -ForegroundColor Yellow
}

Write-Host "------------------------------------"
Write-Host "Processo de organização de imagens concluído."
Write-Host "Verifique as pastas e atualize os caminhos nos seus arquivos JSON e JSX."