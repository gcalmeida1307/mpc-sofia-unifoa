import { useEffect, useState, type CSSProperties, type ReactNode } from "react"
import ProfileMenu from "../features/authentication/ProfileMenu"
import UiIcon, { type IconName } from "../components/UiIcon"

export type ShellPage = "dashboard" | "chat" | "modules" | "upload" | "neural" | "connections" | "pipeline" | "access"
export type ShellProvider = "auto" | "openai" | "gemini" | "claude" | "ollama"
export type ShellModule = { id: string; name: string; icon: string; color: string; docs: string }
export type ShellUser = { user_code: string; name: string; email: string; role: string; demo_mode?: boolean }
export type ShellApiStatus = "checking" | "online" | "offline" | "unauthorized"
type AppShellProps = {
  children: ReactNode; modules: ShellModule[]; activeModule: ShellModule; activePage: ShellPage
  user: ShellUser; dark: boolean; apiOnline: boolean; apiStatus?: ShellApiStatus; provider: ShellProvider
  providerAvailability?: Partial<Record<ShellProvider, boolean>>
  onModuleChange: (id: string) => void; onPageChange: (page: ShellPage) => void
  onThemeChange: () => void; onProviderChange: (provider: ShellProvider) => void
  changePassword: (current: string, next: string) => Promise<void>;
  onLogout: () => void; isAdmin: boolean
}
const navigation: Array<{ id: ShellPage; label: string; icon: IconName }> = [
  { id: "dashboard", label: "Visão geral", icon: "grid" },
  { id: "chat", label: "Conversar com a SOFIA", icon: "chat" },
  { id: "modules", label: "Conhecimento", icon: "library" },
  { id: "upload", label: "Adicionar fontes", icon: "upload" },
  { id: "neural", label: "Rede neural", icon: "network" },
  { id: "connections", label: "Conexões", icon: "link" },
]
const administration: Array<{ id: ShellPage; label: string; icon: IconName }> = [
  { id: "pipeline", label: "Pipeline Explorer", icon: "pipeline" },
  { id: "access", label: "Usuários e acessos", icon: "users" },
]

export default function AppShell({ children, activeModule, activePage, user, dark, apiOnline, apiStatus, provider, providerAvailability, onPageChange, onThemeChange, onProviderChange, onLogout, isAdmin, changePassword }: AppShellProps) {
  const [profileOpen, setProfileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const goToPage = (page: ShellPage) => { onPageChange(page); setMobileOpen(false) }
  const providerEnabled = (name: ShellProvider) => providerAvailability?.[name] !== false
  const connectionStatus = apiStatus ?? (apiOnline ? "online" : "offline")
  const connectionLabel = connectionStatus === "checking" ? "Conectando com a API" : connectionStatus === "unauthorized" ? "Sessão expirada" : connectionStatus === "online" ? "Conectado" : "Sem conexão com a API"
  useEffect(() => {
    if (!mobileOpen) return
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") setMobileOpen(false) }
    window.addEventListener("keydown", close)
    return () => window.removeEventListener("keydown", close)
  }, [mobileOpen])
  const navButton = (item: typeof navigation[number]) => (
    <button key={item.id} className={`nav-item${activePage === item.id ? " selected" : ""}`} type="button" title={collapsed ? item.label : undefined} aria-current={activePage === item.id ? "page" : undefined} onClick={() => goToPage(item.id)}>
      <UiIcon name={item.icon} /><span className="nav-label">{item.label}</span>
      {item.id === "chat" && <small className="nav-ai">IA</small>}
    </button>
  )
  return (
    <div className={dark ? "app sofia-studio dark" : "app sofia-studio"} style={{ "--accent": activeModule.color } as CSSProperties}>
      {mobileOpen && <button className="shell-overlay" type="button" aria-label="Fechar menu" onClick={() => setMobileOpen(false)} />}
      <aside id="sofia-navigation" className={`sidebar${collapsed ? " is-collapsed" : ""}${mobileOpen ? " is-mobile-open" : ""}`} aria-label="Navegação principal">
        <div className="logo"><div className="logo-mark"><UiIcon name="spark" /></div><div className="logo-copy"><strong>SOFIA<span className="brand-dot">.</span></strong><span>GESTÃO INTELIGENTE</span></div><button className="sidebar-toggle" type="button" aria-label={collapsed ? "Expandir navegação" : "Recolher navegação"} aria-expanded={!collapsed} onClick={() => setCollapsed(!collapsed)}><UiIcon name="chevron" style={{ transform: collapsed ? undefined : "rotate(180deg)" }} /></button></div>
        <div className="sidebar-scroll">
          <div className="side-heading">WORKSPACE</div><nav aria-label="Workspace">{navigation.map(navButton)}</nav>
          {isAdmin && <><div className="side-heading">ADMINISTRAÇÃO</div><nav aria-label="Administração">{administration.map(navButton)}</nav></>}
        </div>
        <div className="side-footer"><button type="button" className="profile profile-trigger" aria-label="Abrir meu perfil" onClick={() => setProfileOpen(true)} aria-haspopup="dialog"><div className="profile-initials" aria-hidden="true">{user.name.split(" ").map((part) => part[0]).slice(0, 2).join("")}</div><span><b>{user.name}</b><small>{isAdmin ? "Administrador" : "Workspace pessoal"}</small></span><i className={`profile-status ${connectionStatus === "online" ? "online" : connectionStatus === "checking" ? "checking" : "offline"}`} title={connectionLabel} /></button><div className="mobile-account-actions"><button type="button" onClick={onThemeChange}>{dark ? "Modo claro" : "Modo escuro"}</button><button type="button" onClick={onLogout}>Sair</button></div></div>
      </aside>
      {profileOpen && <ProfileMenu user={user} changePassword={changePassword} onClose={() => setProfileOpen(false)} />}
      <main className="content">
        <header className="topbar">
          {user.demo_mode && <strong style={{color: "#a78bfa", fontSize: 11}}>DEMO LOCAL · DADOS FICTÍCIOS</strong>}
          <button className="mobile-menu-button" type="button" aria-label="Abrir menu" aria-controls="sofia-navigation" aria-expanded={mobileOpen} onClick={() => setMobileOpen(true)}><UiIcon name="menu" /></button>
          <div className="crumb"><span>Workspace</span><UiIcon name="chevron" width="12" /><b>{[...navigation, ...administration].find((item) => item.id === activePage)?.label}</b></div>
          <div className="top-right"><span className={`studio-status ${connectionStatus}`} role="status"><i />{connectionLabel}</span><label className="provider-control"><span className="sr-only">Motor de resposta</span><select className="provider-select" value={provider} onChange={(event) => onProviderChange(event.target.value as ShellProvider)} aria-label="Motor de resposta"><option value="auto">✧ Automático</option>{([['openai', 'OpenAI'], ['gemini', 'Gemini'], ['claude', 'Claude'], ['ollama', 'Ollama']] as const).map(([id, label]) => <option key={id} value={id} disabled={!providerEnabled(id)}>{label}{!providerEnabled(id) ? " · indisponível" : ""}</option>)}</select></label><button type="button" className="studio-button compact" onClick={() => goToPage("chat")}><UiIcon name="spark" width="15" />Conversar</button></div>
        </header>
        {children}
      </main>
    </div>
  )
}
