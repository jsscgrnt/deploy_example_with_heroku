import streamlit as st
import pandas as pd
import base64
import pydeck as pdk
import smtplib
import io

def export_csv(df):
  with io.StringIO() as buffer:
    df.to_csv(buffer)
    return buffer.getvalue()

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Clique aqui para baixar o csv modelo</a>'
    return href

def main():

    df_modelo = pd.read_csv('dataframe_jpt.csv')
    st.image('logocanopy.png', width= 200)
    st.title('Sistema de recebimento de dados')
    st.subheader('Canopy Remote Sensing Solutions')
    st.text('Esta é uma aplicação para padronização do recebimento de dados de parcelas de inventário')
    st.markdown(" ")
    st.markdown(get_table_download_link(df_modelo), unsafe_allow_html=True)
    file = st.file_uploader('Escolha a base de dados que deseja analisar (.csv)', type = 'csv')

    if file is not None:
        st.subheader('Analisando os dados...')
        st.markdown(" ")
        df = pd.read_csv(file,  index_col=False)
        col_names = list(df.columns)
        st.markdown('**Visualizar CSV:**')
        ver_df = st.checkbox('Visualizar')
        if ver_df:
            st.dataframe(pd.DataFrame(df))

        st.markdown("**Espacialização das parcelas...**")
        espacializar = st.checkbox("Espacializar Parcelas")
        if espacializar:
            layer = pdk.Layer(
                'PointCloudLayer',
                df,
                get_position=['lon', 'lat'],
                coverage=1)
            view_state = pdk.ViewState(
                longitude=-55.2643,
                latitude=-16.6864,
                zoom=3,
                min_zoom=1,
                max_zoom=15,
            )
            r = pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                layers=[layer],
                initial_view_state=view_state,
                )
            st.pydeck_chart(r)

        st.markdown("**Checando nome de colunas...**")
        if "User_ID" in col_names:
            st.markdown('Coluna "User_ID" OK!')
            st.markdown("**Enivar dados:**")
            enviar = st.button("Enviar")
            if enviar:
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email.mime.application import MIMEApplication

                from email import encoders
                mail_content = '''Hello,
                        This is a test mail.
                        In this mail we are sending some attachments.
                        The mail is sent using Python SMTP library.
                        Thank You
                        '''

                # The mail addresses and password
                sender_address = 'insira@seu@email' #ficticio
                sender_pass = 'insira@a@senha@do@recebedor' #ficticio
                receiver_address = 'jessicagerente@gmail.com'
                # Setup the MIME
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'A test mail sent by Python. It has an attachment.'
                # The subject line
                # The body and the attachments for the mail
                EXPORTERS = {'download_csv.csv': export_csv}

                message.attach(MIMEText(mail_content, 'plain'))

                for filename in EXPORTERS:
                    attachment = MIMEApplication(EXPORTERS[filename](df))
                    attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
                    message.attach(attachment)

                # Create SMTP session for sending the mail
                session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
                session.starttls()  # enable security
                session.login(sender_address, sender_pass)  # login with mail_id and password
                text = message.as_string()
                session.sendmail(sender_address, receiver_address, text)
                session.quit()
                st.markdown('Arquivo enviado com sucesso!')
        else:
            st.write(
                f' <em style="color: red; font-size: medium">{"ATENÇÃO: "}</em>'
                f'O campo <em style="color: green; font-size: medium">{col_names[0]}</em> está fora do padrão esperado: '
                f'<em style="color: black; font-size: medium">{"idt"}</em>',
                unsafe_allow_html=True)
            st.text("Favor modificar o nome da coluna para 'idt', conforme csv modelo")

if __name__ == "__main__":
    main()

#exemplo de mapa
# st.deck_gl_chart(
#     viewport = {
#         'latitude': -16.6864,
#         'longitude': -49.2643,
#         'zoom': 3,
#     },
#     layers=[{
#         'type': 'HexagonLayer',
#         'data': df,
#         'radius': 200,
#         'elevationScale': 4,
#         'elevationRange': [0, 1000],
#         'pickable': True,
#         'extruded': True,
#     }, {
#         'type': 'ScatterplotLayer',
#         'data': df,
#     }])
