import { useEffect, useRef, useState, type FormEvent } from "react"
import { describeApiError } from "../../services/api-client"

type User = { name: string; email: string; user_code: string; role: string }
export default function ProfileMenu({ user, onClose, changePassword }: { user: User; onClose: () => void; changePassword: (current: string, next: string) => Promise<void> }) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [editing, setEditing] = useState(false)
  const [current, setCurrent] = useState("")
  const [next, setNext] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)
  useEffect(() => { dialog.current?.showModal() }, [])
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setSuccess(false)
    if (next !== confirmation) { setError("A confirmação não corresponde à nova senha."); return }
    if (next === current) { setError("Escolha uma senha diferente da atual."); return }
    setBusy(true)
    try { await changePassword(current, next); setCurrent(""); setNext(""); setConfirmation(""); setEditing(false); setSuccess(true) }
    catch (reason) { setError(describeApiError(reason, "Não foi possível alterar a senha.")) }
    finally { setBusy(false) }
  }
  return <dialog ref={dialog} className="profile-dialog" aria-labelledby="profile-title" onCancel={(event) => { event.preventDefault(); if (!busy) onClose() }}>
    <header><div><small>MINHA CONTA</small><h2 id="profile-title">Seu perfil</h2></div><button type="button" onClick={onClose} disabled={busy} aria-label="Fechar perfil">✕</button></header>
    <dl><div><dt>Nome</dt><dd>{user.name}</dd></div><div><dt>E-mail</dt><dd>{user.email}</dd></div><div><dt>Usuário</dt><dd>{user.user_code}</dd></div><div><dt>Perfil de acesso</dt><dd>{user.role === "admin" ? "Administrador" : "Usuário"}</dd></div></dl>
    {success && <p className="profile-success" role="status">Senha alterada com sucesso.</p>}
    {!editing ? <button className="studio-button" type="button" onClick={() => { setEditing(true); setSuccess(false) }}>Trocar senha</button> : <form onSubmit={submit}>
      <h3>Trocar senha</h3>
      <label>Senha atual<input type="password" autoComplete="current-password" value={current} onChange={e => setCurrent(e.target.value)} required disabled={busy} /></label>
      <label>Nova senha<input type="password" autoComplete="new-password" value={next} onChange={e => setNext(e.target.value)} required disabled={busy} /></label>
      <label>Confirmar nova senha<input type="password" autoComplete="new-password" value={confirmation} onChange={e => setConfirmation(e.target.value)} required disabled={busy} /></label>
      {error && <p role="alert" className="profile-error">{error}</p>}
      <footer><button type="button" disabled={busy} onClick={() => { setEditing(false); setCurrent(""); setNext(""); setConfirmation(""); setError("") }}>Cancelar</button><button type="submit" className="studio-button" disabled={busy}>{busy ? "Salvando…" : "Salvar nova senha"}</button></footer>
    </form>}
  </dialog>
}

