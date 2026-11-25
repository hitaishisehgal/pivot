"""Keras shared trunk with independently named grade and category heads."""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def build_multitask(input_dim, widths=(64,32), dropout=.2, learning_rate=.001,
                    loss_weights=None, l2=0.0):
    inp = keras.Input((input_dim,), name="features")
    x = inp
    for i, width in enumerate(widths):
        x = layers.Dense(width, activation="relu", kernel_regularizer=keras.regularizers.l2(l2), name=f"shared_{i+1}")(x)
        if dropout: x = layers.Dropout(dropout, name=f"dropout_{i+1}")(x)
    grade = layers.Dense(1, activation="sigmoid", name="grade_scaled")(x)
    category = layers.Dense(3, activation="softmax", name="category")(x)
    model = keras.Model(inp, {"grade_scaled": grade, "category": category})
    model.compile(optimizer=keras.optimizers.Adam(learning_rate),
        loss={"grade_scaled": keras.losses.Huber(), "category": "sparse_categorical_crossentropy"},
        loss_weights=loss_weights or {"grade_scaled":1., "category":1.},
        metrics={"grade_scaled":[keras.metrics.MeanAbsoluteError(name="mae")],
                 "category":[keras.metrics.SparseCategoricalAccuracy(name="accuracy")]})
    return model

def build_single_task(input_dim, task, widths=(64,32), dropout=.2, learning_rate=.001, l2=0.0):
    if task not in ("regression","classification"): raise ValueError(task)
    inp=keras.Input((input_dim,),name="features"); x=inp
    for i,width in enumerate(widths):
        x=layers.Dense(width,activation="relu",kernel_regularizer=keras.regularizers.l2(l2),name=f"shared_{i+1}")(x)
        if dropout: x=layers.Dropout(dropout,name=f"dropout_{i+1}")(x)
    if task=="regression":
        out=layers.Dense(1,activation="sigmoid",name="grade_scaled")(x)
        model=keras.Model(inp,out); model.compile(optimizer=keras.optimizers.Adam(learning_rate),loss=keras.losses.Huber(),metrics=[keras.metrics.MeanAbsoluteError(name="mae")])
    else:
        out=layers.Dense(3,activation="softmax",name="category")(x)
        model=keras.Model(inp,out); model.compile(optimizer=keras.optimizers.Adam(learning_rate),loss="sparse_categorical_crossentropy",metrics=[keras.metrics.SparseCategoricalAccuracy(name="accuracy")])
    return model

def fit_multitask(model, x, y_grade, y_class, epochs=200, batch_size=16, validation_split=.2, verbose=0):
    return model.fit(x, {"grade_scaled":y_grade/20., "category":y_class}, epochs=epochs,
        batch_size=batch_size, validation_split=validation_split, verbose=verbose,
        callbacks=[keras.callbacks.EarlyStopping(monitor="val_loss", patience=20, restore_best_weights=True),
                   keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=.5, patience=8, min_lr=1e-5)])

def predict(model, x):
    # Call the already-built model directly. Keras predict() creates a separate
    # traced prediction function and can retrace it repeatedly across CV folds.
    outputs = model(tf.convert_to_tensor(x), training=False)
    outputs = {name: value.numpy() for name, value in outputs.items()}
    grade = (outputs["grade_scaled"].reshape(-1)*20).clip(0,20)
    return grade, outputs["category"]
