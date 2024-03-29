from loss import objectives

def get_val_at_idx(line, idx):
    return line.split()[idx].strip(',()')

if __name__ == '__main__':
    for objective in objectives:
        with open(objective['input_file'], 'r') as input_file, \
            open(objective['output_folder'] + '/train_loss.csv', 'w') as train_loss_file, \
            open(objective['output_folder'] + '/train_acc.csv', 'w') as train_acc_file, \
            open(objective['output_folder'] + '/validation_loss.csv', 'w') as validation_loss_file, \
            open(objective['output_folder'] + '/validation_acc.csv', 'w') as validation_acc_file:
            for line in input_file:
                if objective['train_loss_key'] in line:
                    if 'train_loss_idx' in objective:
                        train_loss = float(get_val_at_idx(line, objective['train_loss_idx']))
                        train_loss_file.write(str(train_loss) + '\n')
                    if 'train_acc_idx' in objective:
                        train_acc = float(get_val_at_idx(line, objective['train_acc_idx']))
                        if objective['acc_in_percentage']:
                            train_acc = train_acc * 0.01
                        train_acc_file.write(str(train_acc) + '\n')
                if objective['validation_loss_key'] in line:
                    if 'validation_loss_idx' in objective:
                        validation_loss = float(get_val_at_idx(line, objective['validation_loss_idx']))
                        validation_loss_file.write(str(validation_loss) + '\n')
                    if 'validation_acc_idx' in objective:
                        validation_acc = float(get_val_at_idx(line, objective['validation_acc_idx']))
                        if objective['acc_in_percentage']:
                            validation_acc = validation_acc * 0.01
                        validation_acc_file.write(str(validation_acc) + '\n')
