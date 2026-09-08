import { useState, type CSSProperties, type ReactNode } from "react"

export type ShellPage = "dashboard" | "chat" | "modules" | "upload" | "neural" | "connections" | "pipeline" | "access"

export type ShellProvider = "auto" | "openai" | "gemini" | "claude" | "ollama"

export type ShellModule = {
  id: string
  name: string
  icon: string
  color: string
  docs: string
}

export type ShellUser = {
  user_code: string
  name: string
  email: string
  role: string
}

type AppShellProps = {
  children: ReactNode
  modules: ShellModule[]
  activeModule: ShellModule
  activePage: ShellPage
  user: ShellUser
  dark: boolean
  apiOnline: boolean
  provider: ShellProvider
  providerAvailability?: Partial<Record<ShellProvider, boolean>>
  onModuleChange: (moduleId: string) => void
  onPageChange: (page: ShellPage) => void
  onThemeChange: () => void
  onProviderChange: (provider: ShellProvider) => void
  onLogout: () => void
  isAdmin: boolean
}

const navigation: Array<{ id: ShellPage; label: string; icon: string }> = [
  { id: "dashboard", label: "Dashboard", icon: "▦" },
  { id: "chat", label: "Chat Sofia", icon: "▱" },
  { id: "modules", label: "Conhecimento", icon: "▱" },
  { id: "upload", label: "Ingestão", icon: "↥" },
  { id: "neural", label: "Rede Neural", icon: "♧" },
  { id: "connections", label: "Conexões & Fluxos", icon: "⎇" },
]

const administration: Array<{ id: ShellPage; label: string; icon: string }> = [
  { id: "pipeline", label: "Pipeline Explorer", icon: "◎" },
  { id: "access", label: "Usuários e acessos", icon: "♙" },
]

function pageLabel(page: ShellPage): string {
  return (
    [...navigation, ...administration].find((item) => item.id === page)
      ?.label ?? "Workspace"
  )
}

export default function AppShell({
  children,
  modules,
  activeModule,
  activePage,
  user,
  dark,
  apiOnline,
  provider,
  providerAvailability,
  onModuleChange,
  onPageChange,
  onThemeChange,
  onProviderChange,
  onLogout,
  isAdmin,
}: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const sidebarClass = [
    "sidebar",
    collapsed ? "is-collapsed" : "",
    mobileOpen ? "is-mobile-open" : "",
  ]
    .filter(Boolean)
    .join(" ")

  const goToPage = (page: ShellPage) => {
    onPageChange(page)
    setMobileOpen(false)
  }

  const goToModule = (moduleId: string) => {
    onModuleChange(moduleId)
    setMobileOpen(false)
  }

  const providerEnabled = (name: ShellProvider) =>
    providerAvailability?.[name] !== false

  return (
    <div
      className={dark ? "app dark" : "app"}
      style={{ "--accent": activeModule.color } as CSSProperties}
    >
      {mobileOpen && (
        <button
          className="shell-overlay"
          type="button"
          aria-label="Fechar menu"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <aside className={sidebarClass} aria-label="Navegação principal">
        <div className="logo">
          <div className="logo-mark" aria-hidden="true">
            S
          </div>
          <div className="logo-copy">
            <strong>S.O.F.I.A.</strong>
            <span>Gestão inteligente</span>
          </div>
          <button
            className="sidebar-toggle"
            type="button"
            aria-label={collapsed ? "Expandir navegação" : "Recolher navegação"}
            aria-expanded={!collapsed}
            onClick={() => setCollapsed((value) => !value)}
          >
            {collapsed ? "›" : "‹"}
          </button>
        </div>

        <div className="sidebar-scroll">
          <div className="side-heading">DOMÍNIOS</div>
          <div className="module-list" aria-label="Módulos RAG">
            {modules.map((module) => (
              <button
                key={module.id}
                className={
                  module.id === activeModule.id
                    ? "module-option selected"
                    : "module-option"
                }
                type="button"
                title={collapsed ? module.name : undefined}
                aria-current={
                  module.id === activeModule.id ? "page" : undefined
                }
                onClick={() => goToModule(module.id)}
                style={
                  module.id === activeModule.id
                    ? { "--module-color": module.color } as CSSProperties
                    : undefined
                }
              >
                <span aria-hidden="true">{module.icon}</span>
                <b>{module.name}</b>
                <small>{module.docs}</small>
                <i aria-hidden="true" />
              </button>
            ))}
          </div>

          <div className="side-divider" />
          <div className="side-heading">WORKSPACE</div>
          <nav aria-label="Workspace">
            {navigation.map((item) => (
              <button
                key={item.id}
                className={
                  activePage === item.id ? "nav-item selected" : "nav-item"
                }
                type="button"
                title={collapsed ? item.label : undefined}
                aria-current={activePage === item.id ? "page" : undefined}
                onClick={() => goToPage(item.id)}
              >
                <span aria-hidden="true">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                <i aria-hidden="true" />
              </button>
            ))}
          </nav>

          {isAdmin && (
            <>
              <div className="side-heading admin-heading">ADMINISTRAÇÃO</div>
              <nav aria-label="Administração">
                {administration.map((item) => (
                  <button
                    key={item.id}
                    className={
                      activePage === item.id ? "nav-item selected" : "nav-item"
                    }
                    type="button"
                    title={collapsed ? item.label : undefined}
                    aria-current={activePage === item.id ? "page" : undefined}
                    onClick={() => goToPage(item.id)}
                  >
                    <span aria-hidden="true">{item.icon}</span>
                    <span className="nav-label">{item.label}</span>
                    <i aria-hidden="true" />
                  </button>
                ))}
              </nav>
            </>
          )}
        </div>

        <div className="side-footer">
          <div className="online" role="status">
            <i className={apiOnline ? "is-online" : "is-offline"} />
            <span>
              {apiOnline ? "Serviços locais online" : "API local indisponível"}
            </span>
          </div>
          <button
            className="theme-button"
            type="button"
            onClick={onThemeChange}
          >
            <span aria-hidden="true">☼</span>
            <span>{dark ? "Modo claro" : "Modo escuro"}</span>
          </button>
          <button className="logout-button" type="button" onClick={onLogout}>
            <span aria-hidden="true">↪</span>
            <span>Sair</span>
          </button>
          <div className="profile">
            <div aria-hidden="true">{user.user_code.slice(-2)}</div>
            <span>
              <b>{user.name}</b>
              <small>
                {user.user_code} · {user.email}
              </small>
            </span>
          </div>
        </div>
      </aside>

      <main className="content">
        {activePage !== "chat" && activePage !== "upload" && (
          <div className={`shell-ambient shell-ambient-${activePage}`} aria-hidden="true">
            <div className="ambient-orb">
              <span className="ambient-orb-ring ring-one" />
              <span className="ambient-orb-ring ring-two" />
              <span className="ambient-orb-ring ring-three" />
              {Array.from({ length: 18 }, (_, index) => (
                <i key={index} style={{ "--node-index": index } as CSSProperties} />
              ))}
            </div>
          </div>
        )}
        <header className="topbar">
          <button
            className="mobile-menu-button"
            type="button"
            aria-label="Abrir menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen(true)}
          >
            ☰
          </button>
          <div className="crumb">
            <span style={{ color: activeModule.color }}>
              {activeModule.icon} &nbsp;{activeModule.name}
            </span>
            <b>{pageLabel(activePage)}</b>
          </div>
          <div className="top-right">
            <span className="precision">
              <i aria-hidden="true">●</i> {activeModule.docs} documentos
            </span>
            <label className="provider-control">
              <span className="sr-only">Motor de resposta</span>
              <select
                className="provider-select"
                value={provider}
                onChange={(event) =>
                  onProviderChange(event.target.value as ShellProvider)
                }
                aria-label="Motor de resposta"
              >
                <option value="auto">Automático</option>
                <option value="openai" disabled={!providerEnabled("openai")}>
                  OpenAI Responses
                  {!providerEnabled("openai") ? " · bloqueado" : ""}
                </option>
                <option value="gemini" disabled={!providerEnabled("gemini")}>
                  Gemini{!providerEnabled("gemini") ? " · bloqueado" : ""}
                </option>
                <option value="claude" disabled={!providerEnabled("claude")}>
                  Claude{!providerEnabled("claude") ? " · bloqueado" : ""}
                </option>
                <option value="ollama" disabled={!providerEnabled("ollama")}>
                  Ollama{!providerEnabled("ollama") ? " · indisponível" : ""}
                </option>
              </select>
            </label>
            <div
              className="top-avatar"
              style={{ background: activeModule.color }}
            >
              S
            </div>
          </div>
        </header>
        {activePage !== "chat" && (
          <div className="workspace-strip" aria-label="Contexto do workspace">
            <div className="workspace-strip-main">
              <span
                className="workspace-strip-dot"
                style={{ background: activeModule.color }}
                aria-hidden="true"
              />
              <strong>{activeModule.name}</strong>
              <span>módulo ativo</span>
              <span className="workspace-strip-separator" aria-hidden="true">
                /
              </span>
              <span>{activeModule.docs} documentos no conhecimento local</span>
            </div>
            <div className="workspace-strip-meta">
              <span className={apiOnline ? "is-online" : "is-offline"}>
                {apiOnline ? "Serviços locais online" : "API local indisponível"}
              </span>
              <span>{provider === "auto" ? "CORE automático" : provider}</span>
            </div>
          </div>
        )}
        {children}
      </main>
    </div>
  )
}
