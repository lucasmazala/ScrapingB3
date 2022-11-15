import sqlite3
import sys
import os
import logging


class Opcao_db():

    def create_connection(self):
        self.connection = None
        try:
            dir_path = os.path.dirname(os.path.realpath(
                __file__))
            filename = os.path.join(dir_path, 'opcoes_db')
            self.connection = sqlite3.connect(filename) # It is needed to pass the full path, so that the code can be runned in the cron job
            logging_name = os.path.join(dir_path, 'logging_opcoes_b3.log')
            logging.basicConfig(filename=logging_name, level=logging.INFO)

        except Exception as e:
            logging.error(self.error_handling())

        return self.connection

    def insert_data(self, serie, strike, data_vencimento, data_dia, call_put):
        try:
            self.connection = self.create_connection()
            params = (serie, strike, data_vencimento, data_dia, call_put)
            self.connection.execute("insert into opcoes_b3 values(?, ?, ?, ?,?)", params)
            self.connection.commit()
            print("Data saved")
        except Exception as e:
            logging.error(self.error_handling())
        finally:
            self.connection.close()

    def retrieve_last_data(self, dia):
        self.connection = self.create_connection()
        last_data = self.connection.cursor()
        last_data.execute("SELECT EXISTS(SELECT 1 FROM opcoes_b3 where data_dia IN (?))", (dia,))
        rows = last_data.fetchall()
        rows = str(rows[0])
        rows = bool(int(rows[1:2]))
        return rows

    def error_handling(self):
        return '{}. {}, line: {}'.format(sys.exc_info()[0],
                                                       sys.exc_info()[1],
                                                       sys.exc_info()[2].tb_lineno)


