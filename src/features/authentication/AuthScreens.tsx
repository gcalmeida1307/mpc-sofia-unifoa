import { useEffect, useState, type FormEvent } from "react"
import { knowledgeModules } from "../../knowledge"
import {
  apiRequest,
  describeApiError,
  SofiaApiError,
} from "../../services/api-client"
import type { AccessRequest, AdminUser, AuthUser } from "../../types/auth"

export function Login({
  onLogin,
}: {
  onLogin: (token: string, user: AuthUser) => void
}) {
  const [identifier, setIdentifier] = useState("")
  const [password, setPassword] = useState("")
  const [otp, setOtp] = useState("")
  const [requires2FA, setRequires2FA] = useState(false)
  const [requesting, setRequesting] = useState(false)
  const [activating, setActivating] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError("")
    try {
      const response = await apiRequest("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier,
          password,
          ...(requires2FA ? { otp } : {}),
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        requires_2fa?: boolean
        token?: string
        user?: AuthUser
      }
      if (data.requires_2fa) {
        setRequires2FA(true)
        setError("Digite o código de 6 dígitos do seu aplicativo autenticador.")
        setBusy(false)
        return
      }
      if (!response.ok || !data.token || !data.user)
        throw new Error(data.detail ?? "Usuário ou senha inválidos")
      onLogin(data.token, data.user)
    } catch (reason) {
      if (reason instanceof SofiaApiError && reason.status === 401) {
        setError(
          requires2FA
            ? "Código 2FA inválido ou expirado. Confira o horário do autenticador e tente novamente."
            : "E-mail, matrícula ou senha inválidos.",
        )
      } else {
        setError(describeApiError(reason, "Usuário ou senha inválidos."))
      }
      setBusy(false)
    }
  }
  if (requesting)
    return (
      <RequestAccess
        onBack={() => {
          setRequesting(false)
          setError("")
        }}
      />
    )
  if (activating)
    return (
      <ActivateAccount
        onBack={() => {
          setActivating(false)
          setError("")
        }}
      />
    )
  if (resetting)
    return (
      <ResetPassword
        onBack={() => {
          setResetting(false)
          setError("")
        }}
      />
    )
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo">S</div>
        <div className="login-kicker">S.O.F.I.A. · PLATAFORMA LOCAL</div>
        <h1>Bem-vindo de volta.</h1>
        <p>Entre com sua matrícula ou e-mail cadastrado.</p>
        <label>
          Usuário ou e-mail
          <input
            type="text"
            value={identifier}
            onChange={(event) => setIdentifier(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {requires2FA && (
          <>
            <div className="login-success">
              Senha aceita. Agora informe o código de 6 dígitos exibido no
              aplicativo autenticador. Esse código não é a sua senha.
            </div>
            <label>
              Código 2FA do autenticador
              <input
                inputMode="numeric"
                pattern="\d{6}"
                maxLength={6}
                value={otp}
                onChange={(event) =>
                  setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                autoComplete="one-time-code"
                required
              />
            </label>
          </>
        )}
        {error && <div className="login-error">{error}</div>}
        <button className="login-submit" disabled={busy}>
          {busy
            ? "Entrando..."
            : requires2FA
              ? "Validar e entrar →"
              : "Entrar no workspace →"}
        </button>
        <button
          type="button"
          className="login-link"
          onClick={() => setRequesting(true)}
        >
          Ainda não tenho acesso · Solicitar conta
        </button>
        <button
          type="button"
          className="login-link"
          onClick={() => setActivating(true)}
        >
          Já fui aprovado · Ativar conta
        </button>
        <button
          type="button"
          className="login-link"
          onClick={() => setResetting(true)}
        >
          Tenho token de reset · Redefinir senha
        </button>
        <small>
          Use a matrícula ou o e-mail cadastrado. A senha é a que foi criada na
          ativação; o autenticador fornece apenas o código temporário do 2FA.
        </small>
      </form>
    </div>
  )
}

export function ResetPassword({ onBack }: { onBack: () => void }) {
  const [userCode, setUserCode] = useState("")
  const [resetToken, setResetToken] = useState("")
  const [password, setPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (password !== confirmation) {
      setError("A confirmação não confere.")
      return
    }
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await apiRequest("/api/auth/password/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          reset_token: resetToken,
          new_password: password,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        message?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível redefinir a senha")
      setMessage(data.message ?? "Senha redefinida. Você já pode entrar.")
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card request-card" onSubmit={submit}>
        <button type="button" className="back-link" onClick={onBack}>
          ← Voltar para o login
        </button>
        <div className="login-logo">S</div>
        <div className="login-kicker">RECUPERAÇÃO DE ACESSO</div>
        <h1>Redefina sua senha.</h1>
        <p>
          Use a matrícula e o token de recuperação fornecidos pela AG000001. O
          token expira em 10 minutos e pode ser usado uma única vez.
        </p>
        <label>
          Matrícula
          <input
            value={userCode}
            onChange={(event) => setUserCode(event.target.value.toUpperCase())}
            placeholder="Ex.: IN000001"
            pattern="[A-Z]{2}\d{6}"
            required
          />
        </label>
        <label>
          Token de recuperação
          <input
            value={resetToken}
            onChange={(event) => setResetToken(event.target.value)}
            autoComplete="one-time-code"
            required
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
          <small>Use maiúscula, minúscula, número e caractere especial.</small>
        </label>
        <label>
          Confirme a nova senha
          <input
            type="password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
        </label>
        {error && <div className="login-error">{error}</div>}
        {message && <div className="login-success">{message}</div>}
        <button className="login-submit" disabled={busy}>
          {busy ? "Redefinindo..." : "Redefinir senha →"}
        </button>
      </form>
    </div>
  )
}

function ScopePicker({
  value,
  onChange,
}: {
  value: string[]
  onChange: (next: string[]) => void
}) {
  const toggle = (scope: string) => {
    if (scope === "CORE") {
      onChange(value.includes("CORE") ? [] : ["CORE"])
      return
    }
    const next = value.filter((item) => item !== "CORE")
    onChange(
      next.includes(scope)
        ? next.filter((item) => item !== scope)
        : [...next, scope],
    )
  }
  return (
    <div className="scope-grid">
      {[
        ["CORE", "Todos os módulos"],
        ...knowledgeModules.map((item) => [item.id, item.name]),
      ].map(([id, label]) => (
        <label
          className={
            value.includes(id) ? "scope-option selected" : "scope-option"
          }
          key={id}
        >
          <input
            type="checkbox"
            checked={value.includes(id)}
            onChange={() => toggle(id)}
          />
          <span>{label}</span>
        </label>
      ))}
    </div>
  )
}

export function RequestAccess({ onBack }: { onBack: () => void }) {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [requestedModule, setRequestedModule] = useState(
    knowledgeModules[0]?.id ?? "",
  )
  const [scopes, setScopes] = useState<string[]>([])
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await apiRequest("/api/auth/requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          requested_module: requestedModule,
          scopes,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        request_code?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível enviar a solicitação")
      setMessage(
        `Solicitação ${data.request_code} enviada. A AG000001 analisará o acesso e enviará a matrícula e o token de ativação por um canal seguro.`,
      )
      setName("")
      setEmail("")
      setScopes([])
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card request-card" onSubmit={submit}>
        <button type="button" className="back-link" onClick={onBack}>
          ← Voltar para o login
        </button>
        <div className="login-logo">S</div>
        <div className="login-kicker">SOLICITAÇÃO DE ACESSO</div>
        <h1>Peça seu acesso.</h1>
        <p>
          Informe seus dados e escolha o alcance desejado. A senha será criada
          somente depois da aprovação.
        </p>
        <label>
          Nome completo
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            autoComplete="name"
            required
          />
        </label>
        <label>
          E-mail
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />
        </label>
        <label>
          Módulo principal da matrícula
          <select
            value={requestedModule}
            onChange={(event) => setRequestedModule(event.target.value)}
          >
            {knowledgeModules.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          <small>
            A matrícula usará as duas primeiras letras do módulo + seis números
            sequenciais.
          </small>
        </label>
        <div className="scope-label">Módulo(s) solicitado(s)</div>
        <ScopePicker value={scopes} onChange={setScopes} />
        {error && <div className="login-error">{error}</div>}
        {message && <div className="login-success">{message}</div>}
        <button className="login-submit" disabled={busy || scopes.length === 0}>
          {busy ? "Enviando..." : "Enviar solicitação →"}
        </button>
        <small>
          Não informe senha agora. Depois da aprovação, use o código e token
          recebidos para criar sua senha e ativar o 2FA.
        </small>
      </form>
    </div>
  )
}

export function FirstAccess({
  authFetch,
  onDone,
  onLogout,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
  onDone: () => void
  onLogout: () => void
}) {
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (newPassword !== confirmation) {
      setError("A confirmação não confere.")
      return
    }
    setBusy(true)
    setError("")
    try {
      const response = await authFetch("/api/auth/password", {
        method: "POST",
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      })
      const data = (await response.json()) as { detail?: string }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível alterar a senha")
      onDone()
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo">S</div>
        <div className="login-kicker">PRIMEIRO ACESSO</div>
        <h1>Proteja sua conta.</h1>
        <p>Defina uma senha pessoal antes de acessar o workspace.</p>
        <label>
          Senha recebida no primeiro acesso
          <input
            type="password"
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
          <small>Use maiúscula, minúscula, número e caractere especial.</small>
        </label>
        <label>
          Confirme a nova senha
          <input
            type="password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
        </label>
        {error && <div className="login-error">{error}</div>}
        <button className="login-submit" disabled={busy}>
          {busy ? "Salvando..." : "Salvar nova senha →"}
        </button>
        <button type="button" className="login-link" onClick={onLogout}>
          Sair
        </button>
      </form>
    </div>
  )
}

export function ActivateAccount({ onBack }: { onBack: () => void }) {
  const [userCode, setUserCode] = useState("")
  const [activationToken, setActivationToken] = useState("")
  const [password, setPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [code, setCode] = useState("")
  const [artifact, setArtifact] = useState<{
    qr_data_uri: string
    secret: string
    otpauth_uri: string
  } | null>(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const createPassword = async (event: FormEvent) => {
    event.preventDefault()
    if (password !== confirmation) {
      setError("A confirmação não confere.")
      return
    }
    setBusy(true)
    setError("")
    try {
      const response = await apiRequest("/api/auth/activation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          activation_token: activationToken,
          new_password: password,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        qr_data_uri?: string
        secret?: string
        otpauth_uri?: string
        message?: string
      }
      if (
        !response.ok ||
        !data.qr_data_uri ||
        !data.secret ||
        !data.otpauth_uri
      )
        throw new Error(data.detail ?? "Não foi possível ativar a conta")
      setArtifact({
        qr_data_uri: data.qr_data_uri,
        secret: data.secret,
        otpauth_uri: data.otpauth_uri,
      })
      setMessage(data.message ?? "Senha criada.")
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  const enable = async () => {
    setBusy(true)
    setError("")
    try {
      const response = await apiRequest("/api/auth/activation/2fa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          activation_token: activationToken,
          code,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        message?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível ativar o 2FA")
      setMessage(data.message ?? "Conta ativada.")
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card request-card" onSubmit={createPassword}>
        {!artifact ? (
          <>
            <button type="button" className="back-link" onClick={onBack}>
              ← Voltar para o login
            </button>
            <div className="login-logo">S</div>
            <div className="login-kicker">ATIVAÇÃO DE CONTA</div>
            <h1>Finalize seu acesso.</h1>
            <p>
              Use a matrícula e o token enviados pela administração. Depois,
              crie sua senha pessoal.
            </p>
            <label>
              Matrícula gerada
              <input
                value={userCode}
                onChange={(event) =>
                  setUserCode(event.target.value.toUpperCase())
                }
                placeholder="Ex.: IN000001"
                pattern="[A-Z]{2}\d{6}"
                required
              />
            </label>
            <label>
              Token de ativação
              <input
                value={activationToken}
                onChange={(event) => setActivationToken(event.target.value)}
                autoComplete="one-time-code"
                required
              />
            </label>
            <label>
              Nova senha
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={8}
                autoComplete="new-password"
                required
              />
              <small>
                Use maiúscula, minúscula, número e caractere especial.
              </small>
            </label>
            <label>
              Confirme a nova senha
              <input
                type="password"
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                minLength={8}
                autoComplete="new-password"
                required
              />
            </label>
            {error && <div className="login-error">{error}</div>}
            <button className="login-submit" disabled={busy}>
              {busy ? "Ativando..." : "Criar senha e continuar →"}
            </button>
          </>
        ) : (
          <>
            <div className="login-logo">S</div>
            <div className="login-kicker">2FA DA SOFIA</div>
            <h1>Escaneie o QR.</h1>
            <p>{message}</p>
            <small>
              O aplicativo autenticador gera somente o código temporário do
              2FA. No login, use a senha criada na etapa anterior e informe o
              código no campo separado.
            </small>
            <img
              className="two-factor-qr"
              src={artifact.qr_data_uri}
              alt="QR Code para configurar o 2FA"
            />
            <b className="qr-caption">
              Se preferir, cadastre este segredo manualmente:
            </b>
            <code className="two-factor-secret">{artifact.secret}</code>
            <small className="two-factor-uri">{artifact.otpauth_uri}</small>
            <label>
              Código exibido no autenticador
              <input
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                required
              />
            </label>
            {error && <div className="login-error">{error}</div>}
            <button
              type="button"
              className="login-submit"
              disabled={busy || code.length !== 6}
              onClick={() => void enable()}
            >
              {busy ? "Validando..." : "Ativar 2FA e concluir →"}
            </button>
            {message.startsWith("Conta ativada") && (
              <button type="button" className="login-link" onClick={onBack}>
                Voltar para o login
              </button>
            )}
          </>
        )}
      </form>
    </div>
  )
}

export function TwoFactorEnrollment({
  authFetch,
  onDone,
  onLogout,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
  onDone: () => void
  onLogout: () => void
}) {
  const [setup, setSetup] = useState<{
    qr_data_uri: string
    secret: string
    otpauth_uri: string
  } | null>(null)
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const prepare = async () => {
    setError("")
    try {
      const response = await authFetch("/api/auth/2fa/setup", {
        method: "POST",
      })
      const data = (await response.json()) as {
        detail?: string
        qr_data_uri?: string
        secret?: string
        otpauth_uri?: string
      }
      if (
        !response.ok ||
        !data.qr_data_uri ||
        !data.secret ||
        !data.otpauth_uri
      )
        throw new Error(data.detail ?? "Não foi possível preparar o 2FA")
      setSetup({
        qr_data_uri: data.qr_data_uri,
        secret: data.secret,
        otpauth_uri: data.otpauth_uri,
      })
    } catch (reason) {
      setError(describeApiError(reason))
    }
  }
  const enable = async () => {
    setBusy(true)
    setError("")
    try {
      const response = await authFetch("/api/auth/2fa/enable", {
        method: "POST",
        body: JSON.stringify({ code }),
      })
      const data = (await response.json()) as { detail?: string }
      if (!response.ok) throw new Error(data.detail ?? "Código inválido")
      onDone()
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <div className="login-card request-card">
        <div className="login-logo">S</div>
        <div className="login-kicker">PROTEÇÃO OBRIGATÓRIA</div>
        <h1>Ative o 2FA.</h1>
        <p>
          Antes de acessar o workspace, adicione a conta SOFIA ao seu
          autenticador.
        </p>
        {!setup ? (
          <>
            <button className="login-submit" onClick={() => void prepare()}>
              Gerar QR Code →
            </button>
            <button className="login-link" onClick={onLogout}>
              Sair
            </button>
          </>
        ) : (
          <>
            <img
              className="two-factor-qr"
              src={setup.qr_data_uri}
              alt="QR Code para configurar o 2FA"
            />
            <b className="qr-caption">
              Escaneie o QR e informe o código gerado.
            </b>
            <code className="two-factor-secret">{setup.secret}</code>
            <small className="two-factor-uri">{setup.otpauth_uri}</small>
            <label>
              Código 2FA
              <input
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                required
              />
            </label>
            <button
              className="login-submit"
              disabled={busy || code.length !== 6}
              onClick={() => void enable()}
            >
              {busy ? "Validando..." : "Ativar 2FA →"}
            </button>
            <button className="login-link" onClick={onLogout}>
              Sair
            </button>
          </>
        )}
        {error && <div className="login-error">{error}</div>}
      </div>
    </div>
  )
}

export function AccessControl({
  authFetch,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}) {
  const [requests, setRequests] = useState<AccessRequest[]>([])
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const [setup, setSetup] = useState<{
    qr_data_uri: string
    secret: string
    otpauth_uri: string
    enabled: boolean
  } | null>(null)
  const [code, setCode] = useState("")
  const load = async () => {
    try {
      const response = await authFetch("/api/auth/requests?status=pending")
      const data = (await response.json()) as {
        requests: AccessRequest[]
        detail?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao carregar solicitações")
      setRequests(data.requests)
    } catch (reason) {
      setError(describeApiError(reason))
    }
  }
  useEffect(() => {
    void load()
  }, [])
  const decide = async (
    item: AccessRequest,
    approve: boolean,
    scopes = item.requested_scopes,
  ) => {
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await authFetch(
        `/api/auth/requests/${item.id}/decision`,
        {
          method: "POST",
          body: JSON.stringify({
            approve,
            scopes: approve ? scopes : [],
            note: approve
              ? "Aprovado pela AG000001"
              : "Rejeitado pela AG000001",
          }),
        },
      )
      const data = (await response.json()) as {
        detail?: string
        user_code?: string
        activation_token?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao decidir solicitação")
      setMessage(
        approve
          ? `Acesso aprovado. Matrícula: ${data.user_code}. Token de ativação: ${data.activation_token}. Entregue o token ao usuário por um canal seguro.`
          : "Solicitação rejeitada.",
      )
      await load()
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  const setup2FA = async () => {
    setError("")
    try {
      const response = await authFetch("/api/auth/2fa/setup", {
        method: "POST",
      })
      const data = (await response.json()) as {
        detail?: string
        qr_data_uri: string
        secret: string
        otpauth_uri: string
        enabled: boolean
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao preparar o 2FA")
      setSetup(data)
      setMessage(
        "Cadastre o QR no aplicativo autenticador e valide o código abaixo.",
      )
    } catch (reason) {
      setError(describeApiError(reason))
    }
  }
  const enable2FA = async () => {
    try {
      const response = await authFetch("/api/auth/2fa/enable", {
        method: "POST",
        body: JSON.stringify({ code }),
      })
      const data = (await response.json()) as { detail?: string }
      if (!response.ok) throw new Error(data.detail ?? "Código inválido")
      setMessage("2FA ativado para AG000001.")
      setSetup(null)
      setCode("")
    } catch (reason) {
      setError(describeApiError(reason))
    }
  }
  return (
    <div className="page-body narrow">
      <h1>
        Controle de <em>Acessos</em>
      </h1>
      <p className="page-subtitle">
        Somente a conta <b>AG000001</b> aprova solicitações e define o módulo
        permitido.
      </p>
      <section className="admin-security">
        <div>
          <h2>Proteção da conta administradora</h2>
          <p>
            O 2FA TOTP é compatível com Google Authenticator, Microsoft
            Authenticator e similares.
          </p>
        </div>
        <button className="neural-run" onClick={() => void setup2FA()}>
          Configurar 2FA
        </button>
        {setup && (
          <div className="two-factor-box">
            <b>Escaneie o QR Code</b>
            <img
              className="two-factor-qr small"
              src={setup.qr_data_uri}
              alt="QR Code para configurar o 2FA da AG000001"
            />
            <b>Segredo para cadastro manual</b>
            <code>{setup.secret}</code>
            <small>{setup.otpauth_uri}</small>
            <div className="two-factor-verify">
              <input
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                placeholder="Código de 6 dígitos"
              />
              <button
                className="neural-run"
                onClick={() => void enable2FA()}
                disabled={code.length !== 6}
              >
                Ativar 2FA
              </button>
            </div>
          </div>
        )}
      </section>
      {error && <div className="login-error">{error}</div>}
      {message && <div className="login-success">{message}</div>}
      <section className="access-list">
        <div className="access-list-heading">
          <h2>Solicitações pendentes</h2>
          <button className="login-link" onClick={() => void load()}>
            Atualizar
          </button>
        </div>
        {requests.length === 0 ? (
          <p>Nenhuma solicitação pendente.</p>
        ) : (
          requests.map((item) => (
            <article className="access-card" key={item.id}>
              <div>
                <b>{item.name}</b>
                <small>
                  {item.email} · {item.request_code}
                </small>
                <span>
                  Matrícula: automática · módulo principal:{" "}
                  {item.requested_module ??
                    "definido pelos módulos solicitados"}
                </span>
                <span>
                  Acesso solicitado:{" "}
                  {item.requested_scopes.includes("CORE")
                    ? "CORE (todos os módulos)"
                    : item.requested_scopes.join(", ")}
                </span>
              </div>
              <div className="access-actions">
                <button
                  className="neural-run"
                  disabled={busy}
                  onClick={() => void decide(item, true)}
                >
                  Aprovar
                </button>
                <button
                  className="neural-run danger"
                  disabled={busy}
                  onClick={() => void decide(item, false)}
                >
                  Rejeitar
                </button>
              </div>
            </article>
          ))
        )}
      </section>
    </div>
  )
}

export function UserAdministration({
  authFetch,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [inactiveDays, setInactiveDays] = useState("90")
  const [resetArtifact, setResetArtifact] = useState<{
    user_code: string
    reset_token: string
    expires_at: number
  } | null>(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const load = async () => {
    try {
      const response = await authFetch("/api/auth/users")
      const data = (await response.json()) as {
        users: AdminUser[]
        inactivity: { inactive_lock_days: number }
        detail?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao carregar usuários")
      setUsers(data.users)
      setInactiveDays(String(data.inactivity.inactive_lock_days))
    } catch (reason) {
      setError(describeApiError(reason))
    }
  }
  useEffect(() => {
    void load()
  }, [])
  const resetPassword = async (user: AdminUser) => {
    setBusy(true)
    setError("")
    setMessage("")
    setResetArtifact(null)
    try {
      const response = await authFetch(
        `/api/auth/users/${user.user_code}/reset`,
        {
          method: "POST",
        },
      )
      const data = (await response.json()) as {
        detail?: string
        reset_token?: string
        expires_at?: number
        user_code?: string
        message?: string
      }
      if (
        !response.ok ||
        !data.reset_token ||
        !data.expires_at ||
        !data.user_code
      )
        throw new Error(
          data.detail ?? "Não foi possível criar o token de reset",
        )
      setResetArtifact({
        user_code: data.user_code,
        reset_token: data.reset_token,
        expires_at: data.expires_at,
      })
      setMessage(data.message ?? "Token de reset criado.")
      await load()
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  const changeStatus = async (user: AdminUser) => {
    const active = !user.active
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await authFetch(
        `/api/auth/users/${user.user_code}/status`,
        {
          method: "POST",
          body: JSON.stringify({
            active,
            reason: active ? undefined : "Bloqueado pela AG000001",
          }),
        },
      )
      const data = (await response.json()) as { detail?: string }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível alterar o status")
      setMessage(
        active
          ? `${user.user_code} reativado.`
          : `${user.user_code} bloqueado.`,
      )
      await load()
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  const savePolicy = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await authFetch("/api/auth/users/inactivity-policy", {
        method: "POST",
        body: JSON.stringify({ inactive_lock_days: Number(inactiveDays) }),
      })
      const data = (await response.json()) as {
        detail?: string
        blocked_now?: number
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível salvar a política")
      setMessage(
        `Política salva. Usuários bloqueados agora: ${data.blocked_now ?? 0}. A AG000001 é isenta.`,
      )
      await load()
    } catch (reason) {
      setError(describeApiError(reason))
    } finally {
      setBusy(false)
    }
  }
  const date = (value?: string | null) =>
    value ? new Date(value).toLocaleString("pt-BR") : "Nunca"
  const expiry = (value: number) =>
    new Date(value * 1000).toLocaleTimeString("pt-BR")
  return (
    <div className="page-body user-admin-page">
      <div className="admin-page-heading">
        <div>
          <h1>
            Administração de <em>usuários</em>
          </h1>
          <p className="page-subtitle">
            Status, sessões, tokens de recuperação e política de inatividade.
          </p>
        </div>
        <button
          className="neural-run"
          onClick={() => void load()}
          disabled={busy}
        >
          Atualizar
        </button>
      </div>
      <section className="admin-token-note">
        <b>Tokens de sessão</b>
        <span>
          O token de sessão é rotacionado automaticamente a cada 10 minutos. Por
          segurança, o painel exibe apenas o fingerprint; nunca expõe o token em
          texto puro. Para recuperação, gere um token descartável abaixo.
        </span>
      </section>
      <form className="admin-policy" onSubmit={savePolicy}>
        <div>
          <h2>Bloqueio por inatividade</h2>
          <small>
            Contas sem login ou atividade acima desse período serão bloqueadas
            automaticamente. A AG000001 não é bloqueada.
          </small>
        </div>
        <label>
          Dias
          <input
            type="number"
            min={1}
            max={3650}
            value={inactiveDays}
            onChange={(event) => setInactiveDays(event.target.value)}
          />
        </label>
        <button className="neural-run" disabled={busy}>
          Salvar política
        </button>
      </form>
      {error && <div className="login-error">{error}</div>}
      {message && <div className="login-success">{message}</div>}
      {resetArtifact && (
        <section className="reset-token-box">
          <b>Token de recuperação — {resetArtifact.user_code}</b>
          <code>{resetArtifact.reset_token}</code>
          <small>
            Entregue por canal seguro. Expira hoje às{" "}
            {expiry(resetArtifact.expires_at)}e não poderá ser exibido novamente
            após sair desta tela.
          </small>
          <button
            className="login-link"
            type="button"
            onClick={() =>
              void navigator.clipboard?.writeText(resetArtifact.reset_token)
            }
          >
            Copiar token
          </button>
        </section>
      )}
      <section className="user-list">
        <div className="access-list-heading">
          <h2>Contas cadastradas ({users.length})</h2>
          <small>Admin protegida: AG000001</small>
        </div>
        {users.map((user) => (
          <article className="user-admin-card" key={user.user_code}>
            <div className="user-admin-main">
              <div className="user-admin-title">
                <span
                  className={user.active ? "status-dot active" : "status-dot"}
                />
                <b>{user.user_code}</b>
                <span
                  className={user.active ? "status-pill active" : "status-pill"}
                >
                  {user.active ? "ativo" : "bloqueado"}
                </span>
                {user.role === "admin" && (
                  <span className="status-pill admin">admin</span>
                )}
              </div>
              <strong>{user.name}</strong>
              <small>{user.email}</small>
              <span>
                Módulos:{" "}
                {user.scopes.includes("CORE")
                  ? "CORE (todos)"
                  : user.scopes.join(", ")}
              </span>
              <span>
                Último login: {date(user.last_login_at)} · atividade:{" "}
                {date(user.last_seen_at)}
              </span>
              {!user.active && user.blocked_reason && (
                <span>Motivo: {user.blocked_reason}</span>
              )}
              <span>
                2FA: {user.two_factor_enabled ? "ativo" : "não configurado"} ·
                sessões ativas: {user.session_count}
              </span>
              {user.tokens.length > 0 && (
                <div className="session-list">
                  {user.tokens.map((token) => (
                    <small key={token.fingerprint}>
                      Sessão {token.fingerprint} · última rotação:{" "}
                      {date(token.last_rotated_at)} · expira:{" "}
                      {new Date(token.expires_at * 1000).toLocaleString(
                        "pt-BR",
                      )}
                    </small>
                  ))}
                </div>
              )}
            </div>
            <div className="user-admin-actions">
              <button
                className="neural-run"
                disabled={busy || !user.active}
                onClick={() => void resetPassword(user)}
              >
                Gerar reset · 10 min
              </button>
              {user.role !== "admin" && (
                <button
                  className="neural-run danger"
                  disabled={busy}
                  onClick={() => void changeStatus(user)}
                >
                  {user.active ? "Bloquear" : "Reativar"}
                </button>
              )}
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}
