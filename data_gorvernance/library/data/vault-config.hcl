storage "file" {
  path = "/home/jovyan/.vault"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = 1
}

ui = true
disable_mlock = true

log_level = "debug"  # ログレベルを設定
log_file  = "/home/jovyan/.vault/log//vault.log"
