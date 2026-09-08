import { useEffect, useState, type DragEvent, type FormEvent } from "react"
import { describeApiError } from "../../services/api-client"

export type KnowledgeModule = {
  id: string
  name: string
  color: string
  docs: string
}

type AuthFetch = (path: string, init?: RequestInit) => Promise<Response>

type OfflineLink = {
  title?: string
  pages?: number
  file_name?: string
  offline_path?: string
  storage?: string
}

export default function Upload({
  mod,
  authFetch,
  onUploaded,
}: {
  mod: KnowledgeModule
  authFetch: AuthFetch
  onUploaded: () => void
}) {
  const [status, setStatus] = useState("")
  const [dragging, setDragging] = useState(false)
  const [url, setUrl] = useState("")
  const [deep, setDeep] = useState(true)
  const [links, setLinks] = useState<OfflineLink[]>([])

  const loadLinks = async () => {
    try {
      const response = await authFetch(`/api/modules/${mod.id}/links`)
      const data = (await response.json()) as { links?: OfflineLink[] }
      setLinks(data.links ?? [])
    } catch {
      setLinks([])
    }
  }

  useEffect(() => {
    void loadLinks()
  }, [mod.id])

  const uploadFile = async (file?: File) => {
    if (!file) return
    setStatus("Enviando e salvando no módulo...")
    const form = new FormData()
    form.append("file", file)
    try {
      const response = await authFetch(`/api/modules/${mod.id}/upload`, {
        method: "POST",
        body: form,
      })
      const data = (await response.json()) as {
        file?: string
        ocr?: { available?: boolean }
      }
      const destination = data.ocr
        ? `knowledge/${mod.id}/imagens · OCR ${
            data.ocr.available ? "disponível" : "indisponível"
          }`
        : `knowledge/${mod.id}/textos`
      setStatus(
        `${data.file ?? file.name} salvo em ${destination} · processamento agendado`,
      )
      onUploaded()
    } catch (error) {
      setStatus(
        `Falha: ${describeApiError(error, "não foi possível enviar o arquivo")}`,
      )
    }
  }

  const submitLink = async (event: FormEvent) => {
    event.preventDefault()
    if (!url.trim()) return
    setStatus(
      `Lendo o link${
        deep ? " e até 10 páginas relacionadas do mesmo domínio" : ""
      }...`,
    )
    try {
      const response = await authFetch(`/api/modules/${mod.id}/links`, {
        method: "POST",
        body: JSON.stringify({ url, max_pages: deep ? 10 : 1, dense: deep }),
      })
      const data = (await response.json()) as {
        link?: { title?: string; pages?: number; storage?: string }
      }
      const link = data.link ?? {}
      setStatus(
        `Documento offline salvo: ${link.title ?? "link capturado"} · ${link.pages ?? 1} página(s) reais · ${
          link.storage === "postgresql" ? "PostgreSQL" : "adaptador local"
        } · processamento agendado`,
      )
      setUrl("")
      await loadLinks()
      onUploaded()
    } catch (error) {
      setStatus(
        `Falha: ${describeApiError(error, "não foi possível ingerir o link")}`,
      )
    }
  }

  const drop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault()
    setDragging(false)
    void uploadFile(event.dataTransfer.files[0])
  }

  return (
    <div className="page-body upload-page">
      <h1>
        Upload de <em>Fontes</em>
      </h1>
      <p className="page-subtitle">
        Tudo é associado ao gestor ativo:{" "}
        <b style={{ color: mod.color }}>knowledge/{mod.id}</b>. A fonte entra no
        RAG e pode atualizar a rede neural.
      </p>
      <section className="ingest-card">
        <h2>Arquivos e imagens</h2>
        <p>
          Imagens entram no módulo e passam por OCR no treinamento e na busca.
        </p>
        <label
          className={dragging ? "drop-zone is-dragging" : "drop-zone"}
          onDragEnter={() => setDragging(true)}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={() => setDragging(false)}
          onDrop={drop}
        >
          ⇧<strong>Arraste arquivos aqui ou clique para selecionar</strong>
          <small>
            PDF · DOCX · TXT · MD · CSV · JSON · XML · YAML · LOG · XLSX · PNG ·
            JPG · WEBP · TIFF · BMP — máx. 50 MB
          </small>
          <input
            type="file"
            hidden
            accept=".pdf,.docx,.txt,.md,.csv,.json,.xml,.yaml,.yml,.log,.xlsx,.png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff"
            onChange={(event) => void uploadFile(event.target.files?.[0])}
          />
        </label>
      </section>
      <section className="ingest-card">
        <h2>Links viram documentos offline</h2>
        <p>
          O conteúdo é capturado em <b>knowledge/{mod.id}/links</b>, entra no
          RAG e é registrado no PostgreSQL quando configurado.
        </p>
        <form className="link-form" onSubmit={submitLink}>
          <input
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://dominio.com/documentacao"
            aria-label="URL da fonte"
            required
          />
          <label className="check-row">
            <input
              type="checkbox"
              checked={deep}
              onChange={(event) => setDeep(event.target.checked)}
            />{" "}
            Pesquisa densa: seguir até 10 páginas reais do mesmo domínio
          </label>
          <button className="neural-run" type="submit">
            Salvar documento offline →
          </button>
        </form>
        {links.length > 0 && (
          <div className="offline-list">
            <strong>Documentos offline deste módulo</strong>
            {links.map((link, index) => (
              <div key={`${link.file_name}-${index}`}>
                <span>{link.title ?? "Link capturado"}</span>
                <small>
                  {link.pages ?? 1} página(s) ·{" "}
                  {link.storage === "postgresql"
                    ? "PostgreSQL + arquivo local"
                    : "arquivo local"}{" "}
                  ·{" "}
                  {link.offline_path ??
                    `knowledge/${mod.id}/links/${link.file_name ?? ""}`}
                </small>
              </div>
            ))}
          </div>
        )}
      </section>
      {status && (
        <div className="upload-status" role="status">
          {status}
        </div>
      )}
    </div>
  )
}
