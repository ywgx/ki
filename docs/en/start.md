## Get Started Immediately

It is recommended to install the `ki` tool globally. Execute it on the Linux host where you manage k8s daily:

```bash
curl xabc.io/ki | bash
```

The above command will download and install two files `/usr/local/bin/ki` and `/etc/profile.d/zki.sh`. Of course, you can also manually download from [github.com/ywgx/ki](https://github.com/ywgx/ki) and place it in an executable path according to your own habits.

!> Note that the default interpreter path for `ki` is `/usr/bin/python3`. Please check the path where python3 is located on your host. If there is a difference, please modify the first line of `/usr/local/bin/ki` to `#!/usr/bin/python3`

## List Current k8s Namespaces

Here are 3 k8s clusters. The current config symlink points to `/root/.kube/kubeconfig-edge`

![](//static.xabc.io/ki/ki-1.png)

## Similar Matching

Most similar matching, `ki sys` matches the kube-system Namespace. Actually, `ki sy` can also match here.

![](//static.xabc.io/ki/ki-2.png)

## Filter Search

Full list string filtering, which can continuously narrow the filtering range. For example, filter and search for a keyword str or a Pod on a certain machine 14.8.

![](//static.xabc.io/ki/ki-3.png)

## Auto-switch $KUBECONFIG

Please note, initially under the edge cluster, when `$ ki test`, because the current k8s cannot find any matching Namespace, it automatically looks for the next one. The 2nd time it finds one - in the test cluster there is a non-empty Namespace called test, and it switches $KUBECONFIG. The real-time terminal prompt shows the current $KUBECONFIG is kubeconfig-test.

![](//static.xabc.io/ki/ki-8.png)

## Actively Switch $KUBECONFIG

Sometimes we need to view a certain Namespace, and this Namespace exists in multiple k8s clusters, so we can actively switch $KUBECONFIG. There are two ways: one is to match and automatically switch in one go in the parameter `ki $k8s.$ns`, the other is to actively switch to the target k8s first `ki -s`

Please note that initially `ki sys` views kube-system under the test cluster, while `ki ho.sys` will view kube-system under the hongkong cluster. ki can parse ho.sys separately, ho can match kubeconfig-hongkong by similarity, and sys can match kube-system by similarity.

![](//static.xabc.io/ki/ki-19.png)

When we have a massive number of k8s clusters, we use `ki -s` to filter, search, and select the target k8s to switch to.

![](//static.xabc.io/ki/ki-20.png)

## **Series of Actions on Target Pod**

Generally, it is recommended that the three types of resource objects Deployment(StatefulSet)/Service/Ingress have the same naming, which is simple and clear, and also has many advantages.

### `$index` Press Enter to directly login to Pod

![](//static.xabc.io/ki/ki-4.png)

### `$index l` Output Pod real-time logs

Output the latest 200 lines by default.

![](//static.xabc.io/ki/ki-5.png)

### `$index l 10000` Output Pod real-time logs

Adding a number after l represents how many lines of the latest logs to output.

![](//static.xabc.io/ki/ki-6.png)

### `$index l chunked` Filter Pod real-time logs

Adding a string after l represents outputting log lines that filter the string.

![](//static.xabc.io/ki/ki-7.png)

### `$index e` Automatically identify resource objects and enter edit mode

![](//static.xabc.io/ki/ki-9.png)

### `$index es` Edit Service resource with the same name as the target Pod

![](//static.xabc.io/ki/ki-10.png)

### `$index ei` Edit Ingress resource with the same name as the target Pod

![](//static.xabc.io/ki/ki-11.png)

### `$index r` Restart target Pod

Please note that what is restarted here is the resource object to which the target Pod belongs.

![](//static.xabc.io/ki/ki-12.png)

### `$index del` Delete target Pod

What is deleted here is the target Pod. Generally, according to k8s scheduling rules, a new one will be pulled up quickly.

![](//static.xabc.io/ki/ki-13.png)

### `$index cle` Clean up the resource object to which the target Pod belongs

!> Please note that what is cleaned up is the resource object to which the target Pod belongs, so cleaning up means complete deletion. Clean (cle) is intentionally designed to require entering three characters, expecting you to understand the meaning of the current action and reduce misoperations.

![](//static.xabc.io/ki/ki-14.png)

## Series of Actions on Other Resources

The above are all output the Pods list of the target Namespace by default, and then select further actions. Of course, we can also directly select the target resource object list, Deployment/StatefulSet/DaemonSet/Service/Ingress/ConfigMap/Secret/PV/PVC, and then the next action is similar to Pod actions, can filter/edit/delete.

- ki test d (output Deployment list)
- ki test f (output StatefulSet list)
- ki test a (output DaemonSet list)
- ki test s (output Service list)
- ki test i (output Ingress list)
- ki test c (output ConfigMap list)
- ki test t (output Secret list)
- ki test v (output PV list)
- ki test p (output PVC list)
- ki test e (output Event)

## Last Selection and Latest Selection

- The `#` symbol represents the last selected object, and like `$index`, it can continue to be followed by actions such as l/e/del/cle
- The `$` symbol represents selecting the latest running Pod object, and like `$index`, it can continue to be followed by actions such as l/e/del/cle

![](//static.xabc.io/ki/ki-25.png)

## Series of Actions on Node Resources

When you want to view the Node hosts of the target k8s, you just need one more parameter n, such as `ki test n` will output the Node machine list. Please note that the middle parameter test still fuzzy matches Namespace. In this case, it represents the k8s host list that contains the non-empty Namespace test.

### `$index` Press Enter to remotely login to the target host by default

Generally, we recommend putting the ssh-key public key data of the control machine on the Node machine for easy direct login.

![](//static.xabc.io/ki/ki-15.png)

### `$index e` Edit Node resource object

![](//static.xabc.io/ki/ki-16.png)

### `$index c` Set target Node resource object as unschedulable, `$index u` Set target Node resource object as schedulable

![](//static.xabc.io/ki/ki-17.png)

## Advanced Operations (Not Necessary)

### Namespace Feature Short String

- `ki` highlighted in red is the Feature Hashing characteristic short string

![](//static.xabc.io/ki/hash.png)

### One-step, login/view logs/edit

In some user scenarios, such as developers or database administrators who only care about a certain Pod or several Pods they are responsible for daily, `ki -i[le] $ns $pod` can match the target Pod in one step.

- `ki -i d sql` -i parameter represents that this operation will login to the matched Pod in one step, d parameter matches Namespace, sql parameter matches the most similar Pod
- `ki -l d sql` -l parameter represents that this operation will view the real-time log of the matched Pod in one step, d parameter matches Namespace, sql parameter matches the most similar Pod
- `ki -e d sql` -e parameter represents that this operation will edit the resource to which the matched Pod belongs in one step, d parameter matches Namespace, sql parameter matches the most similar Pod

![](//static.xabc.io/ki/ki-21.png)

### Follow Directory, Auto-switch

This is a management convention. Please note the consistency between the 2nd field of the 3 kubeconfig file names under the ~/.kube/ directory and the 1st field of the 3 k8s directory names under the /cache/sys/K8S/ directory. Maintaining this naming convention, when in the `K8S` directory, ki starts to identify whether there are corresponding multi-cluster independent management directories, and enters the automatic follow directory switching state. The terminal command prompt in this follow switching state is light blue. If there is a switch, a light red (switch) prompt will appear once. This mode can minimize errors in cluster operations to the maximum extent.

![](//static.xabc.io/ki/ki-22.png)

Temporarily lock to prohibit follow switching and unlock switching. For example, sometimes we expect to apply a certain yml resource in the A cluster directory to the B cluster, so we can temporarily prohibit follow directory automatic switching through `ki -l`, and unlock through `ki -u`. It should be reminded that this kind of lock is only for the follow directory state, and will not prohibit matching Namespace automatic switching. `ki -s` active selection switching is also considered as temporary locking. The locking operation is for 1 hour, and it will automatically unlock after 1 hour.

![](//static.xabc.io/ki/ki-23.png)

## Statistical Analysis of Resource Object Operations

Operation records for each day are stored in $HOME/.history/. .dict is the statistics of historical cluster switching. .last is the cluster of the last switching operation. .name_dict is the historical operation analysis of resource objects operated in each k8s/ns.

- Symbol ~ or ! matches the last operated resource object in the current k8s/ns
- Symbol @ or # matches the most historically operated resource object in the current k8s/ns
- Symbol $ matches the latest released resource object in the current k8s/ns

!> Note that .ns_dict is a non-empty Namespace cache file generated after executing `ki -c`. This cache file can speed up ki's automatic switching. If there are newly created Namespaces in the cluster or they were originally empty but are now non-empty, you need to re-execute `ki -c`.

![](//static.xabc.io/ki/ki-24.png)

## View Help

Actually, just understanding the two usages of Pod login and viewing logs can meet 90% of daily work needs. Other operations will naturally be understood slowly.

![](//static.xabc.io/ki/ki-18.png)
