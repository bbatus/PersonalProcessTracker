import React, {useState} from 'react';
import {View, Text, StyleSheet, TouchableOpacity, Alert} from 'react-native';
import {Task} from '../types';
import {useTaskStore} from '../stores/taskStore';
import {useTheme, Spacing, FontSizes, BorderRadius} from '../utils/theme';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

interface TaskCardProps {
  task: Task;
}

export const TaskCard: React.FC<TaskCardProps> = ({task}) => {
  const theme = useTheme();
  const {markDone, markSkipped, postponeTask} = useTaskStore();
  const [showActions, setShowActions] = useState(false);

  const handleTap = () => {
    if (task.status === 'PENDING') {
      setShowActions(!showActions);
      ReactNativeHapticFeedback.trigger('selection');
    }
  };

  const handleDone = async () => {
    ReactNativeHapticFeedback.trigger('impactLight');
    setShowActions(false);
    await markDone(task.id);
  };

  const handleSkip = async () => {
    ReactNativeHapticFeedback.trigger('impactLight');
    setShowActions(false);
    await markSkipped(task.id);
  };

  const handlePostpone = async () => {
    ReactNativeHapticFeedback.trigger('impactLight');
    setShowActions(false);
    await postponeTask(task.id);
  };

  const getStatusColor = () => {
    switch (task.status) {
      case 'DONE':
        return theme.success;
      case 'SKIPPED':
        return theme.textSecondary;
      default:
        return theme.text;
    }
  };

  const getStatusIcon = () => {
    switch (task.status) {
      case 'DONE':
        return '✓';
      case 'SKIPPED':
        return '⊘';
      default:
        return '○';
    }
  };

  const styles = createStyles(theme);

  return (
    <TouchableOpacity
      style={[
        styles.container,
        task.status !== 'PENDING' && styles.containerCompleted,
      ]}
      onPress={handleTap}
      activeOpacity={0.7}>
      <View style={styles.content}>
        {/* Category Color Indicator */}
        <View
          style={[
            styles.categoryIndicator,
            {backgroundColor: task.category.color},
          ]}
        />

        {/* Task Info */}
        <View style={styles.info}>
          <Text
            style={[
              styles.title,
              task.status !== 'PENDING' && styles.titleCompleted,
              {color: getStatusColor()},
            ]}>
            {getStatusIcon()} {task.title}
          </Text>
          {task.description && (
            <Text style={styles.description}>{task.description}</Text>
          )}
          <Text style={styles.category}>{task.category.name}</Text>
        </View>
      </View>

      {/* Action Buttons */}
      {showActions && task.status === 'PENDING' && (
        <View style={styles.actions}>
          <TouchableOpacity style={styles.actionButton} onPress={handleDone}>
            <Text style={[styles.actionText, {color: theme.success}]}>
              Done
            </Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={handleSkip}>
            <Text style={[styles.actionText, {color: theme.warning}]}>
              Skip
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={handlePostpone}>
            <Text style={[styles.actionText, {color: theme.primary}]}>
              Tomorrow
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </TouchableOpacity>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    container: {
      backgroundColor: theme.card,
      borderRadius: BorderRadius.md,
      marginBottom: Spacing.sm,
      overflow: 'hidden',
    },
    containerCompleted: {
      opacity: 0.6,
    },
    content: {
      flexDirection: 'row',
      padding: Spacing.md,
    },
    categoryIndicator: {
      width: 4,
      borderRadius: 2,
      marginRight: Spacing.md,
    },
    info: {
      flex: 1,
    },
    title: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      marginBottom: Spacing.xs,
    },
    titleCompleted: {
      textDecorationLine: 'line-through',
    },
    description: {
      fontSize: FontSizes.sm,
      color: theme.textSecondary,
      marginBottom: Spacing.xs,
    },
    category: {
      fontSize: FontSizes.xs,
      color: theme.textSecondary,
      textTransform: 'uppercase',
    },
    actions: {
      flexDirection: 'row',
      borderTopWidth: 1,
      borderTopColor: theme.border,
    },
    actionButton: {
      flex: 1,
      padding: Spacing.md,
      alignItems: 'center',
      borderRightWidth: 1,
      borderRightColor: theme.border,
    },
    actionText: {
      fontSize: FontSizes.sm,
      fontWeight: '600',
    },
  });
