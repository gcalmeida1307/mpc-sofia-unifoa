import { type CSSProperties } from "react"
import UiIcon from "../../components/UiIcon"
import type { KnowledgeModule } from "../../knowledge"

type Props = {
  mod: KnowledgeModule
  modules: KnowledgeModule[]
  online: boolean
  onSelectModule: (id: string) => void
  onOpenChat: () => void
  onOpenSources: () => void
}

export default function OverviewCards({ mod, modules, online, onSelectModule, onOpenChat, onOpenSources }: Props) {
  const active = Math.max(0, modules.findIndex((item) => item.id === mod.id))
  const offsets = modules.length >= 5 ? [-2, -1, 0, 1, 2] : modules.map((_, index) => index - Math.floor(modules.length / 2))
  const formats = Object.entries(mod.documentsByType ?? {}).sort((a, b) => b[1] - a[1]).slice(0, 4)
  const total = Object.values(mod.documentsByType ?? {}).reduce((sum, value) => sum + value, 0)
  const switchCard = (direction: number) => {
    if (modules.length) onSelectModule(modules[(active + direction + modules.length) % modules.length].id)
  }
  return (
    <div className="overview-bento">
      <section className="studio-panel knowledge-hero" aria-label="Seu assistente de conhecimento">
        <div className="hero-copy"><span className="studio-eyebrow"><UiIcon name="spark" width="14" /> SEU ASSISTENTE INTELIGENTE</span><h2>Conhecimento que<br />vira <span>possibilidade.</span></h2><p>Conecte suas fontes, encontre respostas e dê o próximo passo com a SOFIA.</p><button className="studio-button" type="button" onClick={onOpenChat}>Vamos conversar <UiIcon name="arrow" width="16" /></button><small className="hero-module"><i style={{ background: mod.color }} />{mod.name} <span>· módulo selecionado</span></small></div>
        <div className="knowledge-sculpture" aria-hidden="true"><div className="sculpture-halo" /><div className="sculpture-orbit orbit-one" /><div className="sculpture-orbit orbit-two" /><div className="sculpture-stack"><div className="sculpture-layer layer-back" /><div className="sculpture-layer layer-middle" /><div className="sculpture-layer layer-front"><UiIcon name="spark" width="60" height="60" /><span>SOFIA</span></div></div><span className="sculpture-node node-one"><UiIcon name="file" /></span><span className="sculpture-node node-two"><UiIcon name="network" /></span><span className="sculpture-node node-three"><UiIcon name="chat" /></span></div>
      </section>
      <section className="studio-panel studio-context" aria-label="Contexto do módulo">
        <div className="studio-panel-heading"><h3>Em foco</h3><span className="studio-tag">MÓDULO ATIVO</span></div>
        <div className="context-heading"><span className="context-icon" style={{ "--module-color": mod.color } as CSSProperties}>{mod.icon}</span><div><h4>{mod.name}</h4><small>{mod.category}</small></div></div><p>{mod.focus}</p>
        <div className="context-metrics"><div><strong>{mod.docs}</strong><span>documentos</span></div><div><strong>{mod.links ?? 0}</strong><span>links associados</span></div></div>
        <div className={`context-connection ${online ? "online" : "offline"}`}><i /><span>{online ? "Conectado ao seu conhecimento" : "Aguardando conexão com a API"}</span></div>
      </section>
      <section className="studio-panel module-showcase" aria-label="Escolha seu domínio">
        <div className="studio-panel-heading"><div><h3>Um universo de conhecimento</h3><small>Escolha o domínio da sua próxima descoberta.</small></div><span className="studio-tag">{modules.length} DOMÍNIOS</span></div>
        <div className="module-deck">{offsets.map((offset) => {
          const item = modules[(active + offset + modules.length) % modules.length]
          if (!item) return null
          return <button key={item.id} type="button" className={`domain-card${offset === 0 ? " is-active" : ""}`} style={{ "--card-color": item.color, "--card-position": offset, "--card-depth": Math.abs(offset) } as CSSProperties} onClick={() => onSelectModule(item.id)} aria-label={`Selecionar ${item.name}`} aria-pressed={item.id === mod.id}><span className="domain-card-icon" aria-hidden="true">{item.icon}</span><span className="domain-card-category">{item.category}</span><strong>{item.name}</strong><span className="domain-card-footer">{item.docs} fontes <UiIcon name="arrow" width="16" /></span><span className="card-watermark" aria-hidden="true">{item.icon}</span></button>
        })}</div>
        <div className="deck-controls"><button type="button" aria-label="Domínio anterior" disabled={modules.length < 2} onClick={() => switchCard(-1)}><UiIcon name="chevron" width="15" style={{ transform: "rotate(180deg)" }} /></button><span aria-live="polite">{String(active + 1).padStart(2, "0")} <i>/ {String(modules.length).padStart(2, "0")}</i></span><button type="button" aria-label="Próximo domínio" disabled={modules.length < 2} onClick={() => switchCard(1)}><UiIcon name="chevron" width="15" /></button></div>
      </section>
      <section className="studio-panel source-overview" aria-label="Composição das fontes">
        <div className="studio-panel-heading"><div><h3>Suas fontes, conectadas</h3><small>Conhecimento disponível neste domínio.</small></div><UiIcon name="library" /></div>
        <div className="source-format-list">{formats.length ? formats.map(([format, count], index) => <div className="source-format" key={format}><span className={`format-icon format-${index}`}><UiIcon name="file" width="15" /></span><div><span>{format.toUpperCase()}</span><div className="format-meter"><i style={{ width: `${Math.round(count / Math.max(total, 1) * 100)}%`, "--format-color": ['#9d7cff', '#38d9bb', '#f5a95f', '#ed77b6'][index] } as CSSProperties} /></div></div><strong>{count}</strong></div>) : <div className="studio-empty"><UiIcon name="library" width="28" height="28" /><span>{online ? "Tudo começa com uma boa fonte." : "Conecte a API para visualizar suas fontes."}</span></div>}</div>
        <button className="source-callout" type="button" onClick={onOpenSources}><span><UiIcon name="upload" width="17" />Adicionar conhecimento</span><UiIcon name="arrow" width="16" /></button>
      </section>
    </div>
  )
}

