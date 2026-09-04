import { Component, type ErrorInfo, type ReactNode } from "react"

type ErrorBoundaryProps = { children: ReactNode }
type ErrorBoundaryState = { hasError: boolean }

export default class AppErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Keep the diagnostic local and free of application data. A future
    // telemetry adapter can correlate this with a request id if available.
    console.error("SOFIA render error", error.name, info.componentStack)
  }

  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <main className="fatal-error-screen" role="alert">
        <div className="fatal-error-card">
          <div className="login-logo" aria-hidden="true">S</div>
          <div className="login-kicker">SOFIA · RECUPERAÇÃO</div>
          <h1>Esta tela precisa ser recarregada.</h1>
          <p>
            O workspace encontrou um erro inesperado. Seus dados continuam no
            servidor local; recarregue a página para tentar novamente.
          </p>
          <button type="button" className="login-submit" onClick={() => window.location.reload()}>
            Recarregar workspace →
          </button>
        </div>
      </main>
    )
  }
}

