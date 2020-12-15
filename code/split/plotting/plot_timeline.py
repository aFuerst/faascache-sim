import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
# [2020-08-14T20:17:11.042Z] POST /api/v1/namespaces/_/actions/cnn blocking=true&result=true
# [2020-08-14T20:17:11.371Z] [[36mContainerPool[0m] received run request, Run(ExecutableWhiskAction/alftest/cnn@0.0.1,alftest/cnn@0.0.1?message={},None)
# [2020-08-14T20:17:11.495Z] [[36mContainerPool[0m] starting action ExecutableWhiskAction/alftest/cnn@0.0.1, state cold, cold hits: 1, warm hits: 0
# [2020-08-14T20:17:13.104Z] [[36mDockerContainer[0m] sending initialization to ContainerId(4d6599cbc63e07685a991fc9308ba9a48ea73d9b17193c851273b202212f41a1)
# [2020-08-14T20:17:15.781Z] [[36mDockerContainer[0m] initialization result: ok [marker:invoker_activationInit_finish:4738:2673]
# [2020-08-14T20:17:15.784Z] [[36mDockerContainer[0m] sending arguments to /alftest/cnn at ContainerId(4d6599cbc63e07685a991fc9308ba9a48ea73d9b17193c851273b202212f41a1)
# [2020-08-14T20:17:19.010Z] [[36mDockerContainer[0m] running result: ok [marker:invoker_activationRun_finish:7968:3225]
# [2020-08-14T20:17:19.045Z] [[36mMessagingActiveAck[0m] posted result of activation c7c9797ee4094b9e89797ee4095b9efc
# [2020-08-14T20:17:19.051Z] [[36mLeanBalancer[0m] received result ack for 'c7c9797ee4094b9e89797ee4095b9efc'

# total_latency: 8.076243877410889
# {'body': {'import_done': 1597450635.7567608, 'script_start': 1597450633.8385937, 'latency': 2.2863097190856934, 'cold': True, 'msg': 'good'}}
# init_time: 1.9181671142578125
fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
post = datetime.strptime("2020-08-14T20:17:11.042Z", fmt)
recv = datetime.strptime("2020-08-14T20:17:11.371Z", fmt)
start = datetime.strptime("2020-08-14T20:17:11.495Z", fmt)
start_init = datetime.strptime("2020-08-14T20:17:13.104Z", fmt)

init_script = datetime.strptime("2020-08-14T20:17:15.781Z", fmt).timestamp() - 1.9181671142578125
init_script = datetime.fromtimestamp(init_script)

done_init = datetime.strptime("2020-08-14T20:17:15.781Z", fmt)
send_args = datetime.strptime("2020-08-14T20:17:15.784Z", fmt)
result = datetime.strptime("2020-08-14T20:17:19.010Z", fmt)
ret = datetime.strptime("2020-08-14T20:17:19.045Z", fmt)
ack = datetime.strptime("2020-08-14T20:17:19.051Z", fmt)

print("\n")
total_latency = 8.076243877410889
init_time = 1.9181671142578125
script_latency = 2.2863097190856934

p_t = post.timestamp()

labels = ["POST", "Pool Recv", "Starting", "Begin Init", "Script Init", "Script Exec", "Return Result"]
times = [post, recv, start, start_init, init_script, send_args, ack]
fig, ax1 = plt.subplots()
fig.set_size_inches(5,3)

for i, item in enumerate(times):
    left = item.timestamp() - p_t
    if not i+1 == len(times):
        width = times[i+1].timestamp() - item.timestamp()
    else:
        width = item.timestamp() - post.timestamp()
        width = total_latency - width
    print(labels[i], width, left)
    # if i % 2 == 0:
    #     ymin = 0
    #     ymax = 0.75
    #     ax1.annotate(labels[i], xy=(left, ymin),
    #                 xytext=(-3, np.sign(ymin)*3), textcoords="offset points",
    #                 horizontalalignment="right",
    #                 verticalalignment="bottom" if ymin > 0 else "top")

    # else:
    #     ymin = 1.25
    #     ymax = 2
    #     ax1.annotate(labels[i], xy=(left, ymax),
    #                 xytext=(-3, np.sign(ymax)*3), textcoords="offset points",
    #                 horizontalalignment="right",
    #                 verticalalignment="bottom" if ymax > 0 else "top")

    # ax1.vlines([left], ymin=ymin, ymax=ymax, color="tab:red")  # The vertical stems.

    ax1.barh(y=[1], left=[left], width=[width], height=[0.5])

# for d, l, r in zip(dates, levels, names):
#     ax.annotate(r, xy=(d, l),
#                 xytext=(-3, np.sign(l)*3), textcoords="offset points",
#                 horizontalalignment="right",
#                 verticalalignment="bottom" if l > 0 else "top")

# remove y axis and spines
ax1.get_yaxis().set_visible(False)
for spine in ["left", "top", "right"]:
    ax1.spines[spine].set_visible(False)
ax1.set_xlim([-1,9])
save = "../figs/timeline.png"
ax1.set_xlabel("Time (s)")
plt.savefig(save, bbox_inches="tight")


