"""
Serviço de Notificações por E-mail — SGT
Feature adicionada na mudança de escopo (Sprint 3).

Responsável por enviar alertas automáticos quando:
  - O prazo de uma tarefa está próximo (menos de 48 horas).
  - O status de uma tarefa é alterado por outro membro da equipe.

Em produção, configure as variáveis de ambiente:
    SGT_EMAIL_REMETENTE — e-mail de envio (ex: noreply@techflow.com)
    SGT_EMAIL_SENHA      — senha do remetente (ou App Password)
    SGT_SMTP_HOST        — servidor SMTP (padrão: smtp.gmail.com)
    SGT_SMTP_PORTA       — porta SMTP (padrão: 587)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


# Configurações do servidor SMTP (lidas de variáveis de ambiente)
SMTP_HOST = os.getenv("SGT_SMTP_HOST", "smtp.gmail.com")
SMTP_PORTA = int(os.getenv("SGT_SMTP_PORTA", "587"))
EMAIL_REMETENTE = os.getenv("SGT_EMAIL_REMETENTE", "noreply@techflow.com")
EMAIL_SENHA = os.getenv("SGT_EMAIL_SENHA", "")


class NotificacaoService:
    """
    Serviço responsável pelo envio de notificações por e-mail.

    Utiliza SMTP com TLS para garantir a segurança no envio.
    Em ambiente de testes, o cliente SMTP pode ser injetado via mock.
    """

    def __init__(self, smtp_client=None):
        """
        Inicializa o serviço.

        Args:
            smtp_client: Cliente SMTP opcional (usado em testes para mock).
        """
        self._smtp_client = smtp_client

    def _get_smtp(self):
        """
        Retorna o cliente SMTP configurado.
        Se um mock foi injetado, usa-o; caso contrário, cria conexão real.
        """
        if self._smtp_client:
            return self._smtp_client
        # Conexão real com o servidor SMTP
        servidor = smtplib.SMTP(SMTP_HOST, SMTP_PORTA)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
        return servidor

    def _montar_mensagem(self, destinatario: str,
                         assunto: str, corpo: str) -> MIMEMultipart:
        """
        Monta o objeto de mensagem de e-mail com cabeçalhos formatados.

        Args:
            destinatario (str): E-mail do destinatário.
            assunto (str): Assunto do e-mail.
            corpo (str): Corpo do e-mail em texto simples.

        Returns:
            MIMEMultipart: Mensagem pronta para envio.
        """
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain", "utf-8"))
        return msg

    def notificar_prazo_proximo(self, tarefa) -> bool:
        """
        Envia alerta quando o prazo da tarefa está a menos de 48 horas.

        Args:
            tarefa: Objeto Tarefa com atributos titulo, prazo e usuario_email.

        Returns:
            bool: True se o e-mail foi enviado, False caso contrário.
        """
        # Verifica se há e-mail e prazo configurados
        if not tarefa.usuario_email or not tarefa.prazo:
            return False

        # Verifica se o prazo está próximo (menos de 48 horas)
        try:
            prazo_dt = datetime.strptime(tarefa.prazo, "%d/%m/%Y")
            limite = datetime.now() + timedelta(hours=48)
            if prazo_dt > limite:
                return False  # Prazo ainda distante, não notifica
        except ValueError:
            return False  # Formato de data inválido

        assunto = f"[SGT] ⏰ Prazo próximo: {tarefa.titulo}"
        corpo = (
            f"Olá!\n\n"
            f"A tarefa '{tarefa.titulo}' tem prazo em {tarefa.prazo} "
            f"e está próxima do vencimento.\n\n"
            f"Prioridade: {tarefa.prioridade}\n"
            f"Status atual: {tarefa.status}\n\n"
            f"Acesse o sistema para atualizá-la:\n"
            f"http://localhost:5000\n\n"
            f"— TechFlow Solutions"
        )

        return self._enviar(tarefa.usuario_email, assunto, corpo)

    def notificar_mudanca_status(self, tarefa,
                                 status_anterior: str,
                                 alterado_por: str) -> bool:
        """
        Envia alerta quando o status de uma tarefa é alterado.

        Args:
            tarefa: Objeto Tarefa com o novo status já aplicado.
            status_anterior (str): Status antes da alteração.
            alterado_por (str): E-mail de quem fez a alteração.

        Returns:
            bool: True se o e-mail foi enviado, False caso contrário.
        """
        if not tarefa.usuario_email:
            return False

        # Não notifica se o próprio responsável alterou o status
        if tarefa.usuario_email == alterado_por:
            return False

        assunto = f"[SGT] 🔄 Status atualizado: {tarefa.titulo}"
        corpo = (
            f"Olá!\n\n"
            f"A tarefa '{tarefa.titulo}' teve seu status alterado.\n\n"
            f"Status anterior: {status_anterior}\n"
            f"Novo status:     {tarefa.status}\n"
            f"Alterado por:    {alterado_por}\n\n"
            f"Acesse o sistema para mais detalhes:\n"
            f"http://localhost:5000\n\n"
            f"— TechFlow Solutions"
        )

        return self._enviar(tarefa.usuario_email, assunto, corpo)

    def _enviar(self, destinatario: str, assunto: str, corpo: str) -> bool:
        """
        Realiza o envio do e-mail via SMTP.

        Args:
            destinatario (str): E-mail de destino.
            assunto (str): Assunto da mensagem.
            corpo (str): Conteúdo da mensagem.

        Returns:
            bool: True se enviado com sucesso, False em caso de erro.
        """
        try:
            msg = self._montar_mensagem(destinatario, assunto, corpo)
            servidor = self._get_smtp()
            servidor.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
            return True
        except Exception:
            # Em produção, registrar o erro em log
            return False
