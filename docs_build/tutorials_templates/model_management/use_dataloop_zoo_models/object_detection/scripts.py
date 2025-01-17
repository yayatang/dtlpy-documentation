def func1():
    # !pip install torch torchvision imgaug "scikit-image<0.18"
    import matplotlib.pyplot as plt
    from PIL import Image
    import numpy as np
    import dtlpy as dl
    from dtlpy.ml import train_utils


def func2():
    filters = dl.Filters(resource=dl.FiltersResource.MODEL, use_defaults=False)
    filters.add(field='scope', values='public')
    dl.models.list(filters=filters).print()
    # get the public model
    model = dl.models.get(model_name='pretrained-yolo-v5-small')


def func3():
    package = dl.packages.get(package_id=model.package_id)
    adapter = package.build(module_name='model-adapter')
    adapter.load_from_model(model_entity=model)


def func4():
    item = dl.items.get(item_id='611e174e4c09acc3c5bb81d3')
    annotations = adapter.predict_items([item], with_upload=True)
    image = np.asarray(Image.open(item.download()))
    plt.imshow(item.annotations.show(image,
                                     thickness=5))
    print('Classes found: {}'.format([ann.label for ann in annotations[0]]))


def func5():
    project = dl.projects.create('Fruit - Model Mgmt')
    dataset = project.datasets.create('Fruit')
    dataset.to_df()
    _ = dataset.items.upload(local_path='../../../../assets/sample_datasets/FruitImage/items/*',
                             local_annotations_path='../../../../assets/sample_datasets/FruitImage/json')
    dataset.add_labels(label_list=['orange', 'banana', 'apple'])


def func6():
    pages = dataset.items.list()
    num_items = pages.items_count

    train_proportion = 0.8
    val_proportion = 0.2

    train_partitions = [0] * round(train_proportion * num_items)
    val_partitions = [1] * round(val_proportion * num_items)

    partitions = train_partitions + val_partitions
    random.shuffle(partitions)

    dataset.items.make_dir(directory='/train')
    dataset.items.make_dir(directory='/val')

    item_count = 0
    for item in pages.all():
        if partitions[item_count] == 0:
            item.move(new_path='/train')
        elif partitions[item_count] == 1:
            item.move(new_path='/val')
        item_count += 1

    subsets = {'train': dl.Filters(field='dir', values='/train'),
               'validation': dl.Filters(field='dir', values='/val')}

    dataset.metadata['system']['subsets'] = {
        'train': json.dumps(dl.Filters(field='dir', values='/train').prepare()),
        'validation': json.dumps(dl.Filters(field='dir', values='/validation').prepare()),
    }
    dataset.update()

    cloned_dataset = train_utils.prepare_dataset(dataset=dataset,
                                                 filters=None,
                                                 subsets=subsets)
    # if you want to lock the dataset for future reproducibility, use:
    # cloned_dataset.set_readonly()


def func7():
    new_model = model.clone(model_name='fruits-model',
                            dataset=cloned_dataset,
                            project_id=project.id)
    # create an Item Artifact to save snapshot in your project
    artifact = dl.LocalArtifact(filepath='<dummy filepath>',
                                package_name=package.name,
                                model_name=model_name)

    new_model.configuration = {'weights_filename': 'model.pth',
                               'batch_size': 16,
                               'start_epoch': 0,
                               'num_epochs': 2,
                               'input_size': 256,
                               'id_to_label_map': {(v - 1): k for k, v in cloned_dataset.instance_map.items()}
                               }


def func8():
    adapter.load_from_snapshot(snapshot=new_snapshot)
    root_path, data_path, output_path = adapter.prepare_training()


def func9():
    print("Training {!r} with snapshot {!r} on data {!r}".format(model.name, new_snapshot.id, data_path))

    adapter.train(data_path=data_path,
                  output_path=output_path)


def func10():
    adapter.save_to_model(local_path=output_path,
                          replace=True)


def func11():
    adapter.model.artifacts.list_content()


def func12():
    item = dl.items.get(item_id='6110d4a41467ded7a8c2a23d')
    annotations = adapter.predict_items([item], with_upload=True)
    image = Image.open(item.download())
    plt.imshow(item.annotations.show(image,
                                     thickness=5))
    print('Classes found: {}'.format([ann.label for ann in annotations[0]]))
