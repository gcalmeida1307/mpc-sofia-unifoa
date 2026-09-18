import { useRef, useState, type CSSProperties } from "react"
import type { KnowledgeModule } from "../../knowledge"

export default function ModuleDocumentCard({ item, selected, onOpen }: { item: KnowledgeModule; selected: boolean; onOpen: () => void }) {
  const [flipped, setFlipped] = useState(false)
  const front = useRef<HTMLButtonElement>(null)
  const back = useRef<HTMLButtonElement>(null)
  const turn = (value: boolean) => {
    setFlipped(value)
    requestAnimationFrame(() => (value ? back : front).current?.focus())
  }
  return <article className={`document-flip${flipped ? " is-flipped" : ""}`} style={{ "--module-color": item.color } as CSSProperties} onKeyDown={(event) => { if (event.key === "Escape" && flipped) turn(false) }}>
    <div className="document-flip-inner">
      <button ref={front} type="button" className={`rag-card document-face document-front${selected ? " active" : ""}`} inert={flipped} aria-hidden={flipped} aria-label={`Ver documentos de ${item.name}`} onClick={() => turn(true)}>
        <span className="rag-icon">{item.icon}</span><h3>{item.name}</h3><small>{item.category}</small><p>{item.docs} documentos presentes</p><footer><span>Ver documentos</span><b aria-hidden="true">↻</b></footer>
      </button>
      <section className="document-face document-back" inert={!flipped} aria-hidden={!flipped} aria-label={`Documentos de ${item.name}`}>
        <header><div><small>ACERVO DO MÓDULO</small><h3>{item.name}</h3></div><button ref={back} type="button" onClick={() => turn(false)} aria-label={`Voltar ao cartão ${item.name}`}>↶ Voltar</button></header>
        <div className="document-scroll" tabIndex={flipped ? 0 : -1} role="region" aria-label={`Lista de documentos de ${item.name}`}>
          {item.files === undefined ? <p>Lista indisponível. Verifique a conexão com a API.</p> : item.files.length === 0 ? <p>Este módulo ainda não tem documentos. Adicione fontes para começar.</p> : <ul>{item.files.map((file, index) => <li key={`${file}-${index}`}><span aria-hidden="true">▤</span><span>{file}</span><small>{file.split(".").pop()?.toUpperCase()}</small></li>)}</ul>}
        </div>
        <footer><span>{item.files?.length ?? "—"} arquivos</span><button type="button" onClick={onOpen}>Entrar no módulo →</button></footer>
      </section>
    </div>
  </article>
}

