# Ingestão

Formatos atuais: PDF, DOCX, XLSX, CSV, JSON, XML, YAML, LOG, TXT, MD e imagens
suportadas pelo Tesseract. PDF textual usa extração nativa; OCR só é usado
quando a extração é insuficiente. Imagens dependem do Tesseract instalado e
mostram o estado real da capacidade.

Cada documento recebe hash do arquivo, versão, status, qualidade, resumo,
palavras-chave, entidades, conceitos, relações e perguntas sugeridas. Arquivos
inválidos são movidos para `quarantine/` e podem ser reprocessados pelo
Pipeline Explorer administrativo.
