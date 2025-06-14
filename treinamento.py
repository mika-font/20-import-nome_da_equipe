import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import joblib

# Carrega os dados
data = pd.read_csv('dados_mao.csv', header=0)
X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# Divide em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treina o modelo
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

# Avalia
print("Acurácia:", model.score(X_test, y_test))

# Salva o modelo
joblib.dump(model, 'modelo_mao_knn.pkl')