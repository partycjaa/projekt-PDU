ct = pd.crosstab(df["member_casual"], df["rideable_type"], normalize="index")*100
ct.plot(kind="bar", colormap="Pastel2", figsize=(8,6))
plt.title("rideable type vs member_casual")
plt.xlabel("Użytkownik")
plt.ylabel("Procent")
plt.tight_layout()
plt.savefig("member_casual.png")

ct = pd.crosstab(df["distance_bin"], df["rideable_type"], normalize="index")*100
ct.plot(kind="bar", colormap="Pastel2", figsize=(8,6))
plt.title("rideable type vs distance_bin")
plt.xlabel("Dystans")
plt.ylabel("Procent")
plt.tight_layout()
plt.savefig("dystans.png")
