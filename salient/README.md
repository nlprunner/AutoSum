# Salient
__Salient__ : To _predict_ and _select_ concepts of main characters for generating summaries. In this step, we create and evaluation two methods.

One of them is learning-to-rank. The other one is BRNN.

## LTR
* __Constructing dateset__ : Annotation is the similarity between phrases from summaries and phrases from stories. Each sample is including three types of features,
| type      | name      | description   |
| --------- | --------- | ------------- |
| word      | embedding |               |
| paragraph | position  |               |
| story     | postion   |               |
* __Model and Evaluation__ : SVM_rank
